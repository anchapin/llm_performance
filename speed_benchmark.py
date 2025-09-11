import ollama
import time
import statistics

def benchmark_speed(model_name: str, prompt: str, options: dict):
    """
    Performs a speed benchmark on a given Ollama model.

    Args:
        model_name (str): The name of the model to benchmark.
        prompt (str): The prompt to use for the benchmark.
        options (dict): A dictionary of Ollama options (e.g., {'num_gpu': 999}).

    Returns:
        dict: A dictionary containing TTFT and TPS metrics.
    """
    # --- Warm-up run to load the model ---
    print(f"Performing warm-up for {model_name}...")
    try:
        ollama.generate(model=model_name, prompt=".", options=options)
    except Exception as e:
        print(f"Error during warm-up for {model_name}: {e}")
        return {"error": str(e)}

    # --- TTFT Measurement (Client-Side) ---
    ttfts =
    for _ in range(3): # Average over 3 runs for stability
        start_time = time.perf_counter()
        stream = ollama.generate(
            model=model_name,
            prompt=prompt,
            options=options,
            stream=True
        )
        for chunk in stream:
            if chunk['response']:
                end_time = time.perf_counter()
                ttfts.append((end_time - start_time) * 1000) # Convert to ms
                break
        # Consume the rest of the stream
        for _ in stream:
            pass

    avg_ttft = statistics.mean(ttfts) if ttfts else 0

    # --- TPS Measurement (Server-Side) ---
    response_obj = ollama.generate(
        model=model_name,
        prompt=prompt,
        options=options,
        stream=False
    )

    eval_count = response_obj.get('eval_count', 0)
    eval_duration = response_obj.get('eval_duration', 1) # Avoid division by zero

    tps = (eval_count / (eval_duration / 1_000_000_000)) if eval_duration > 0 else 0

    return {
        "avg_ttft_ms": round(avg_ttft, 2),
        "tps": round(tps, 2)
    }

if __name__ == '__main__':
    # Example Usage
    model_to_test = "llama3:8b-instruct"
    test_options = {'num_gpu': 999, 'temperature': 0.0}
    standard_prompt = "Write a Python function to calculate the Fibonacci sequence up to n."

    print(f"Starting speed benchmark for model: {model_to_test}")
    speed_metrics = benchmark_speed(model_to_test, standard_prompt, test_options)
    print(f"Speed Benchmark Results for {model_to_test}:")
    print(f"  - Average Time to First Token (TTFT): {speed_metrics.get('avg_ttft_ms')} ms")
    print(f"  - Tokens per Second (TPS): {speed_metrics.get('tps')}")