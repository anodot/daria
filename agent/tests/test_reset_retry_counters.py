import os
import subprocess


def test_reset_retry_counters():
    # if the script is not working the test will fail with an exception
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'agent', 'scripts', 'reset_retry_counters.py')
    try:
        subprocess.check_output(['python', path], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        print("Status: FAIL", exc.returncode, exc.output)
        raise
