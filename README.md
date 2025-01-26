# DeepSeek R1 ARC-AGI Evaluation

This repository contains code to evaluate DeepSeek R1's performance on the Abstraction and Reasoning Corpus (ARC) challenge. The evaluation is performed using Ollama for local model inference.

## Overview

The Abstraction and Reasoning Corpus (ARC) is a benchmark designed to measure general fluid intelligence in AI systems. This project provides tools to:
- Load and process ARC tasks
- Present them to a locally running DeepSeek R1 model via Ollama
- Evaluate the model's responses
- Generate detailed performance metrics

## Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai) installed locally
- DeepSeek R1 model pulled in Ollama

## Setup

1. Clone the repository:
```bash
git clone https://github.com/raztronaut/deepseek-r1-arc-agi-eval.git
cd deepseek-r1-arc-agi-eval
```

2. Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

3. Ensure you have the DeepSeek R1 model in Ollama:
```bash
ollama pull deepseek-r1
```

## Running the Evaluation

1. Run the evaluation script:
```bash
python3 evaluate_deepseek.py
```

By default, the script evaluates the first 5 tasks. You can modify this by changing `num_tasks` in `main()`.

2. Results will be saved to `evaluation_results.json`, containing:
- Overall accuracy
- Per-task performance
- Detailed model outputs and expected outputs

## Project Structure

- `evaluate_deepseek.py`: Main evaluation script
- `requirements.txt`: Python dependencies
- `data/`: Directory containing ARC tasks (from the original ARC repository)
  - `training/`: Training tasks
  - `evaluation/`: Evaluation tasks

## Implementation Details

The evaluation process:
1. Loads ARC tasks from JSON files
2. For each task:
   - Formats training examples and test input into a prompt
   - Sends the prompt to DeepSeek R1 via Ollama
   - Parses the model's response into a grid format
   - Compares with the expected output
   - Records results and metrics

The prompt engineering is designed to:
- Clearly present the pattern recognition task
- Provide structured examples
- Request specific output format
- Enforce constraints (numbers 0-9, grid dimensions)

## Results Format

The evaluation generates a JSON file with:
```json
{
    "correct": <number_of_correct_solutions>,
    "total": <total_number_of_test_cases>,
    "tasks": [
        {
            "task_id": <task_identifier>,
            "correct": <number_correct_for_this_task>,
            "total": <number_of_test_cases_for_this_task>,
            "details": [
                {
                    "test_case": <test_case_number>,
                    "correct": <boolean>,
                    "model_output": <grid>,
                    "expected_output": <grid>
                }
            ]
        }
    ]
}
```

## Acknowledgments

- Original ARC dataset: [Abstraction and Reasoning Corpus](https://github.com/fchollet/ARC)
- DeepSeek R1 model
- Ollama project
