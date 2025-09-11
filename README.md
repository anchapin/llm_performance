## LLM Performance — Run using the provided Dockerfile

This repository contains a few Python scripts used for measuring LLM performance. The included `Dockerfile` is intentionally minimal: it sets `WORKDIR /app` and uses `CMD ["python"]`, but it does not copy any repository files into the image. The intended workflow is to build the image and then bind-mount your project directory into the container at runtime.

This README explains how to build the image and run the scripts from macOS (zsh).

Assumptions
- You have Docker installed and can run `docker build` / `docker run` locally.
- You will mount the repository into the container because the Dockerfile does not copy files in.

Quick checklist
- Build the image: Done locally using `docker build`.
- Run a script: bind-mount the repo into `/app` and run `python <script>`.

Build the Docker image

From the repository root (where the `Dockerfile` is):

```bash
docker build -t llm_perf:latest .
```

Run a script (no network)

The Dockerfile is minimal and no files are copied into the image. Mount the current directory into `/app` and run the Python script. The examples below run the container with no network access (`--network none`) to match the intention in the Dockerfile comments; remove that flag if you need network access.

Examples (macOS / zsh):

# Run the main experiment runner
```bash
docker run --rm -it \
  -v "$(pwd)":/app -w /app \
  --network none \
  llm_perf:latest python run_experiment.py
```

# Run the speed benchmark
```bash
docker run --rm -it -v "$(pwd)":/app -w /app --network none llm_perf:latest python speed_benchmark.py
```

# Run the code-eval benchmark
```bash
docker run --rm -it -v "$(pwd)":/app -w /app --network none llm_perf:latest python code_eval_benchmark.py
```

# Analyze results
```bash
docker run --rm -it -v "$(pwd)":/app -w /app --network none llm_perf:latest python analyze_results.py
```

Passing arguments
- Add arguments after the script name. Example:

```bash
docker run --rm -it -v "$(pwd)":/app -w /app --network none llm_perf:latest python run_experiment.py --help
```

If your scripts require Python packages
- If the scripts depend on third-party packages, create a `requirements.txt` in the repo root and install them at container runtime (or modify the Dockerfile to install them at build time). Example (install at runtime):

```bash
docker run --rm -it -v "$(pwd)":/app -w /app --network none llm_perf:latest \
  sh -c "pip install -r requirements.txt && python run_experiment.py"
```

Notes / Troubleshooting
- The image uses Python 3.10 (from `python:3.10-slim`). Confirm the Python version in the container with:

```bash
docker run --rm -it llm_perf:latest python -c 'import sys; print(sys.version)'
```

- If a script needs network access, remove `--network none` from the `docker run` command (or set an appropriate network). The Dockerfile comment states the container is intended to run without network access.
- If a script expects files in a subdirectory, ensure those files are present in your host workspace before mounting.

Requirements coverage
- Create a README with build/run instructions: Done.

If you want, I can also:
- Add a small `requirements.txt` if you provide the deps, or
- Update the `Dockerfile` to copy files and install dependencies at image build time (recommended for reproducible builds).

That's it — the steps above will let you run any of the included Python scripts inside the minimal container provided by the `Dockerfile`.
