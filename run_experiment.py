import csv
import pandas as pd
from speed_benchmark import benchmark_speed
from code_eval_benchmark import benchmark_coding

# --- Experiment Configuration ---
MODELS_TO_TEST = [
    "deepseek-coder:6.7b-instruct",
    "llama3:8b-instruct",
    "codellama:13b-instruct"
]
QUANTIZATIONS = ["q4_K_M", "q5_K_M", "q8_0"]
GPU_LAYERS = 
STANDARD_PROMPT = "Write a Python function to calculate the Fibonacci sequence up to n."
RESULTS_FILE = "benchmark_results.csv"

def run_full_experiment():
    """Runs the entire suite of benchmarks and saves results."""
    
    # Initialize CSV file
    fieldnames = [
        "model_base", "quantization", "num_gpu", "avg_ttft_ms", "tps",
        "humaneval_pass@1", "mbpp_pass@1"
    ]
    with open(RESULTS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    # Iterate through all configurations
    for model_base in MODELS_TO_TEST:
        for quant in QUANTIZATIONS:
            for gpu_layer_count in GPU_LAYERS:
                model_name = f"{model_base}-{quant}" if quant else model_base
                
                print(f"\n--- Starting benchmark for: {model_name} with {gpu_layer_count} GPU layers ---")

                options = {'num_gpu': gpu_layer_count, 'temperature': 0.0}
                
                # Run Speed Benchmark
                speed_results = benchmark_speed(model_name, STANDARD_PROMPT, options)
                if "error" in speed_results:
                    print(f"Skipping due to error: {speed_results['error']}")
                    continue

                # Run Coding Benchmarks
                humaneval_results = benchmark_coding(model_name, options, "humaneval")
                mbpp_results = benchmark_coding(model_name, options, "mbpp")

                # Consolidate and log results
                result_row = {
                    "model_base": model_base,
                    "quantization": quant,
                    "num_gpu": gpu_layer_count,
                    **speed_results,
                    **humaneval_results,
                    **mbpp_results
                }
                
                with open(RESULTS_FILE, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerow(result_row)
                
                print(f"--- Finished benchmark for: {model_name} with {gpu_layer_count} GPU layers ---")
                print(pd.DataFrame([result_row]))

if __name__ == "__main__":
    run_full_experiment()