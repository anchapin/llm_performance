import csv

SAMPLE_ROWS = [
    {
        "model_base": "llama3:8b-instruct",
        "quantization": "q4_K_M",
        "num_gpu": 999,
        "avg_ttft_ms": 120.5,
        "tps": 250.0,
        "humaneval_pass@1": 42.5,
        "mbpp_pass@1": 60.0
    },
    {
        "model_base": "deepseek-coder:6.7b-instruct",
        "quantization": "q4_K_M",
        "num_gpu": 999,
        "avg_ttft_ms": 98.3,
        "tps": 310.2,
        "humaneval_pass@1": 38.0,
        "mbpp_pass@1": 55.0
    },
    {
        "model_base": "codellama:13b-instruct",
        "quantization": "q5_K_M",
        "num_gpu": 0,
        "avg_ttft_ms": 200.1,
        "tps": 95.0,
        "humaneval_pass@1": 50.0,
        "mbpp_pass@1": 70.0
    }
]

RESULTS_FILE = "benchmark_results.csv"


def write_sample():
    fieldnames = [
        "model_base", "quantization", "num_gpu", "avg_ttft_ms", "tps",
        "humaneval_pass@1", "mbpp_pass@1"
    ]
    with open(RESULTS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in SAMPLE_ROWS:
            writer.writerow(row)
    print(f"Wrote sample results to {RESULTS_FILE}")


if __name__ == '__main__':
    write_sample()
