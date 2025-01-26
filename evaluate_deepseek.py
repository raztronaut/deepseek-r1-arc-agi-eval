import json
import os
import asyncio
from typing import List, Dict, Any
from pathlib import Path
import ollama
import time

class ARCEvaluator:
    def __init__(self):
        self.training_path = Path("data/training")
        self.evaluation_path = Path("data/evaluation")
        self.timeout = 30  # timeout in seconds
        
    def load_task(self, task_path: Path) -> Dict[str, Any]:
        """Load a single ARC task from JSON file."""
        with open(task_path, 'r') as f:
            return json.load(f)
    
    def format_grid(self, grid: List[List[int]]) -> str:
        """Format a grid into a string representation."""
        return '\n'.join([' '.join(map(str, row)) for row in grid])
    
    def create_prompt(self, task: Dict[str, Any], test_input: List[List[int]]) -> str:
        """Create a prompt for the model including training examples and test input."""
        prompt = "You are an expert at solving abstract reasoning challenges. Your task is to analyze patterns in grids and generate the correct output grid.\n\n"
        prompt += "Given these training examples:\n\n"
        
        # Add training examples
        for idx, example in enumerate(task['train'], 1):
            prompt += f"Example {idx}:\nInput Grid:\n{self.format_grid(example['input'])}\n"
            prompt += f"Output Grid:\n{self.format_grid(example['output'])}\n\n"
        
        # Add test input
        prompt += f"Now, given this new input grid:\n{self.format_grid(test_input)}\n\n"
        prompt += "Rules:\n"
        prompt += "1. Analyze the pattern in the training examples\n"
        prompt += "2. Apply the same pattern to the new input\n"
        prompt += "3. Respond with ONLY the output grid using space-separated numbers and newlines\n"
        prompt += "4. Each number should be between 0-9\n"
        prompt += "5. Ensure the dimensions match the pattern from examples\n\n"
        prompt += "Output Grid:"
        
        return prompt
    
    def parse_model_output(self, output: str) -> List[List[int]]:
        """Parse the model's output string into a grid."""
        try:
            # Find the first occurrence of digits and newlines
            lines = []
            for line in output.split('\n'):
                # Skip lines until we find one with digits
                if any(c.isdigit() for c in line):
                    lines.append(line)
                # Stop if we find a non-digit line after finding digits
                elif lines:
                    break
            
            # Convert to grid
            grid = []
            for line in lines:
                # Extract only the digits and spaces
                cleaned_line = ''.join(c for c in line if c.isdigit() or c.isspace())
                # Split and convert to integers
                row = [int(num) for num in cleaned_line.split()]
                if row:  # Only add non-empty rows
                    grid.append(row)
            
            return grid
        except:
            return []
    
    def evaluate_task(self, task: Dict[str, Any], model_output: List[List[int]], 
                     expected_output: List[List[int]]) -> bool:
        """Check if the model's output matches the expected output exactly."""
        if not model_output or len(model_output) != len(expected_output):
            return False
        
        for row_model, row_expected in zip(model_output, expected_output):
            if len(row_model) != len(row_expected):
                return False
            if row_model != row_expected:
                return False
        return True
    
    async def call_model_with_timeout(self, prompt: str) -> str:
        """Call the model with a timeout."""
        try:
            response = await asyncio.wait_for(
                ollama.chat(
                    model='deepseek-r1',
                    messages=[{'role': 'user', 'content': prompt}],
                    stream=False
                ),
                timeout=self.timeout
            )
            return response['message']['content']
        except asyncio.TimeoutError:
            print(f"Request timed out after {self.timeout} seconds")
            return ""
        except Exception as e:
            print(f"Error calling model: {str(e)}")
            return ""
    
    async def run_evaluation(self, num_tasks: int = None):
        """Run evaluation on the test set."""
        results = {
            'correct': 0,
            'total': 0,
            'tasks': []
        }
        
        eval_files = list(self.evaluation_path.glob('*.json'))
        if num_tasks:
            eval_files = eval_files[:num_tasks]
        
        for task_path in eval_files:
            start_time = time.time()
            task = self.load_task(task_path)
            task_result = {
                'task_id': task_path.stem,
                'correct': 0,
                'total': len(task['test']),
                'details': []
            }
            
            print(f"\nStarting task {task_path.stem}...")
            
            for test_idx, test_case in enumerate(task['test']):
                prompt = self.create_prompt(task, test_case['input'])
                print(f"Processing test case {test_idx + 1}...")
                
                # Call model with timeout
                model_response = await self.call_model_with_timeout(prompt)
                
                if not model_response:
                    print("Skipping this test case due to model error")
                    continue
                
                parsed_output = self.parse_model_output(model_response)
                is_correct = self.evaluate_task(task, parsed_output, test_case['output'])
                
                if is_correct:
                    task_result['correct'] += 1
                
                detail = {
                    'test_case': test_idx + 1,
                    'correct': is_correct,
                    'model_output': parsed_output,
                    'expected_output': test_case['output']
                }
                task_result['details'].append(detail)
                
                print(f"Test case result: {'✓' if is_correct else '✗'}")
                if not is_correct:
                    print("Expected:")
                    print(self.format_grid(test_case['output']))
                    print("Got:")
                    print(self.format_grid(parsed_output))
            
            results['tasks'].append(task_result)
            results['total'] += task_result['total']
            results['correct'] += task_result['correct']
            
            elapsed_time = time.time() - start_time
            print(f"\nTask {task_path.stem} complete: {task_result['correct']}/{task_result['total']} correct")
            print(f"Time taken: {elapsed_time:.2f} seconds")
            
            # Save intermediate results
            with open('evaluation_results_partial.json', 'w') as f:
                json.dump(results, f, indent=2)
        
        return results

async def main():
    evaluator = ARCEvaluator()
    
    print("Starting evaluation...")
    print("Will evaluate first 5 tasks with 30-second timeout per model call")
    print("Results will be saved after each task")
    
    try:
        results = await evaluator.run_evaluation(num_tasks=5)
        
        print("\nFinal Evaluation Results:")
        print(f"Total Correct: {results['correct']}/{results['total']}")
        print(f"Accuracy: {results['correct']/results['total']*100:.2f}%")
        
        with open('evaluation_results.json', 'w') as f:
            json.dump(results, f, indent=2)
            
    except KeyboardInterrupt:
        print("\nEvaluation interrupted by user")
        print("Partial results have been saved to evaluation_results_partial.json")
    except Exception as e:
        print(f"\nError during evaluation: {str(e)}")
        print("Check evaluation_results_partial.json for any saved results")

if __name__ == "__main__":
    asyncio.run(main()) 