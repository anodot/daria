import os
import subprocess

from agent import cli


def test_send_to_bc(cli_runner):
    # if the script is not working the test will fail with an exception
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'agent', 'scripts', 'send_to_bc.py')
    try:
        subprocess.check_output(['python', path], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        print("Status: FAIL", exc.returncode, exc.output)
        raise
