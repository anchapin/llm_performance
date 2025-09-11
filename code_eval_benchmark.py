import ollama
import evaluate
import os
import re
import docker
from datasets import load_dataset

# --- Security Warning ---
# This script executes untrusted code. It uses Docker for sandboxing.
# Ensure Docker is installed and running.
os.environ = "1"

def sanitize_code(model_output: str) -> str:
    """Extracts Python code from a markdown block."""
    match = re.search(r"```python\n(.*?)```", model_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback for models that don't use markdown
    return model_output.strip()

def execute_in_sandbox(code: str, test: str) -> bool:
    """Executes code and tests in a secure Docker container."""
    client = docker.from_env()
    
    full_script = f"{code}\n\n{test}"
    
    try:
        container = client.containers.run(
            'python:3.10-slim',
            command=['python', '-c', full_script],
            detach=True,
            mem_limit='256m',
            cpu_shares=1,
            network_disabled=True
        )
        result = container.wait(timeout=10) # 10-second timeout
        exit_code = result.get('StatusCode', 1)
        container.remove(force=True)
        return exit_code == 0
    except docker.errors.ContainerError as e:
        # Test failed or code had an error
        container.remove(force=True)
        return False
    except Exception as e:
        # Timeout or other Docker error
        if 'container' in locals():
            container.remove(force=True)
        return False

def benchmark_coding(model_name: str, options: dict, benchmark_name: str = "humaneval"):
    """
    Performs a coding proficiency benchmark.
    
    Args:
        model_name (str): The name of the model to benchmark.
        options (dict): Ollama options.
        benchmark_name (str): "humaneval" or "mbpp".

    Returns:
        dict: A dictionary containing the pass@1 score.
    """
    if benchmark_name == "humaneval":
        dataset = load_dataset("openai_humaneval", split="test")
        prompt_key = "prompt"
        test_key = "test"
    elif benchmark_name == "mbpp":
        dataset = load_dataset("mbpp", "sanitized", split="test")
        prompt_key = "prompt"
        test_key = "test_list"
    else:
        raise ValueError("Unsupported benchmark name")

    prompt_template = (
        "You are an expert Python programmer. Your task is to complete the function defined below.\n"
        "Read the docstring carefully and provide the full, correct implementation.\n"
        "Only return the complete Python function in a single code block. Do not include any explanations."
        "\n\n{problem}"
    )

    passed_count = 0
    total_count = len(dataset)

    for i, problem in enumerate(dataset):
        print(f"Running problem {i+1}/{total_count} for {model_name} on {benchmark_name}...")
        
        prompt_content = problem[prompt_key]
        if benchmark_name == "mbpp":
            # MBPP needs the test list joined
            tests = "\n".join(problem[test_key])
        else:
            tests = problem[test_key]
        
        full_prompt = prompt_template.format(problem=prompt_content)

        response = ollama.generate(
            model=model_name,
            prompt=full_prompt,
            options=options,
            stream=False
        )
        
        generated_code = sanitize_code(response['response'])
        
        # HumanEval prompt includes the function definition, so we need to add it to the test
        if benchmark_name == "humaneval":
            full_code_to_test = prompt_content + generated_code
        else: # MBPP prompt is just a description
            full_code_to_test = generated_code

        if execute_in_sandbox(full_code_to_test, tests):
            passed_count += 1
            print(f"  -> Problem {i+1}: PASSED")
        else:
            print(f"  -> Problem {i+1}: FAILED")

    pass_at_1 = (passed_count / total_count) * 100 if total_count > 0 else 0
    
    return {f"{benchmark_name}_pass@1": round(pass_at_1, 2)}

if __name__ == '__main__':
    # Example Usage
    model_to_test = "deepseek-coder:6.7b-instruct"
    test_options = {'num_gpu': 999, 'temperature': 0.0}

    print(f"Starting HumanEval benchmark for model: {model_to_test}")
    coding_metrics = benchmark_coding(model_to_test, test_options, "humaneval")
    print(f"Coding Benchmark Results for {model_to_test}:")
    print(f"  - HumanEval pass@1: {coding_metrics.get('humaneval_pass@1')}%")