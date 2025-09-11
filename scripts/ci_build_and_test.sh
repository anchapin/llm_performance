#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE_NAME="llm_perf:ci_test"

echo "Building Docker image ${IMAGE_NAME}..."
docker build -t "${IMAGE_NAME}" "${REPO_DIR}"

echo "Running smoke experiment inside container (will write benchmark_results.csv)..."
docker run --rm -v "${REPO_DIR}:/app" -w /app "${IMAGE_NAME}" python run_smoke_experiment.py

echo "Running analysis inside container..."
docker run --rm -v "${REPO_DIR}:/app" -w /app "${IMAGE_NAME}" python analyze_results.py

echo "Checking generated output files..."
for f in figure1_speed_vs_accuracy.png figure2_quantization_impact.png figure3_gpu_offload_impact.png; do
  if [ ! -f "${REPO_DIR}/$f" ]; then
    echo "Missing expected file: $f"
    exit 2
  fi
done

echo "CI build and smoke tests completed successfully."
