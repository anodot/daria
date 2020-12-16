import os
import subprocess

from agent import cli
from .conftest import INPUT_FILES_DIR


def test_antomation(cli_runner):
    dir_path = os.path.join(INPUT_FILES_DIR, 'antomation')
    try:
        subprocess.check_output(['agent', 'apply', '-d', dir_path], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        print("Status: FAIL", exc.returncode, exc.output)
        raise
    cli_runner.invoke(cli.pipeline.delete, ['test_mongo_pipeline_antomation'], catch_exceptions=False)
    cli_runner.invoke(cli.source.delete, ['test_mongo_antomation'], catch_exceptions=False)
