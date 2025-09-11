import os
import subprocess
import sys

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def dependencies_available():
    try:
        import pandas  # noqa: F401
        import matplotlib  # noqa: F401
        import seaborn  # noqa: F401
        return True
    except Exception:
        return False


def run_no_docker_smoke():
    if not dependencies_available():
        print('SKIP: required Python packages (pandas, matplotlib, seaborn) are not installed')
        return 0

    # Ensure matplotlib uses a headless backend
    env = os.environ.copy()
    env.setdefault('MPLBACKEND', 'Agg')

    # Run the smoke experiment to write the CSV
    subprocess.run([sys.executable, os.path.join(REPO_DIR, 'run_smoke_experiment.py')], check=True, env=env)

    # Run the analysis to generate PNGs
    subprocess.run([sys.executable, os.path.join(REPO_DIR, 'analyze_results.py')], check=True, env=env)

    # Check outputs
    missing = []
    for fname in ['figure1_speed_vs_accuracy.png', 'figure2_quantization_impact.png', 'figure3_gpu_offload_impact.png']:
        if not os.path.exists(os.path.join(REPO_DIR, fname)):
            missing.append(fname)

    if missing:
        print('FAIL: missing output files:', ', '.join(missing))
        return 2

    print('PASS: smoke experiment and analysis completed, outputs found')
    return 0


def main():
    code = run_no_docker_smoke()
    sys.exit(code)


if __name__ == '__main__':
    main()
