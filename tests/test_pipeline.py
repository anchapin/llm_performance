import os
import subprocess
import pytest

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IMAGE_NAME = 'llm_perf:ci_test'


def docker_available() -> bool:
    try:
        subprocess.run(['docker', '--version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


@pytest.mark.skipif(not docker_available(), reason='Docker is required for this test')
def test_build_run_and_analyze(tmp_path):
    # Build image
    subprocess.run(['docker', 'build', '-t', IMAGE_NAME, REPO_DIR], check=True)

    # Run smoke experiment to write CSV
    subprocess.run([
        'docker', 'run', '--rm', '-v', f"{REPO_DIR}:/app", '-w', '/app', IMAGE_NAME,
        'python', 'run_smoke_experiment.py'
    ], check=True)

    # Run analysis
    subprocess.run([
        'docker', 'run', '--rm', '-v', f"{REPO_DIR}:/app", '-w', '/app', IMAGE_NAME,
        'python', 'analyze_results.py'
    ], check=True)

    # Check that expected output files exist
    for fname in ['figure1_speed_vs_accuracy.png', 'figure2_quantization_impact.png', 'figure3_gpu_offload_impact.png']:
        assert os.path.exists(os.path.join(REPO_DIR, fname)), f"Expected output {fname} not found"
import os
import shutil
import subprocess
import pytest

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IMAGE_NAME = 'llm_perf:ci_test'


def docker_available() -> bool:
    try:
        subprocess.run(['docker', '--version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


@pytest.mark.skipif(not docker_available(), reason='Docker is required for this test')
def test_build_run_and_analyze(tmp_path):
    # Build image
    subprocess.run(['docker', 'build', '-t', IMAGE_NAME, REPO_DIR], check=True)

    # Run smoke experiment to write CSV
    subprocess.run([
        'docker', 'run', '--rm', '-v', f"{REPO_DIR}:/app", '-w', '/app', IMAGE_NAME,
        'python', 'run_smoke_experiment.py'
    ], check=True)

    # Run analysis
    subprocess.run([
        'docker', 'run', '--rm', '-v', f"{REPO_DIR}:/app", '-w', '/app', IMAGE_NAME,
        'python', 'analyze_results.py'
    ], check=True)

    # Check that expected output files exist
    for fname in ['figure1_speed_vs_accuracy.png', 'figure2_quantization_impact.png', 'figure3_gpu_offload_impact.png']:
        assert os.path.exists(os.path.join(REPO_DIR, fname)), f"Expected output {fname} not found"
*** End Patch
