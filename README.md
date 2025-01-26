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

There are two evaluation scripts available:

### 1. Standard Evaluation
```bash
python3 evaluate_deepseek.py
```
This script runs the evaluation and shows results after each task is complete.

### 2. Streaming Evaluation (Recommended)
```bash
python3 evaluate_deepseek_stream.py
```
This version shows the model's reasoning process in real-time, which is helpful to:
- Monitor the model's thought process
- Verify the model is actively working
- Understand how it approaches each task
- Debug any potential issues

Both scripts will:
- Evaluate the first 5 tasks by default
- Save results to `evaluation_results.json`
- Save intermediate results to `evaluation_results_partial.json`
- Show accuracy metrics at the end

## Project Structure

- `evaluate_deepseek.py`: Standard evaluation script
- `evaluate_deepseek_stream.py`: Evaluation script with real-time reasoning output
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
