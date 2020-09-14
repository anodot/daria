import os
import subprocess

from agent import cli


def test_antomation(cli_runner):
    # if the script is not working the test will fail with an exception
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'agent', 'scripts', 'antomation', 'populate_sources_and_pipelines.py')
    subprocess.check_output(['python', path])
    cli_runner.invoke(cli.pipeline.delete, ['test_mongo_pipeline_antomation'], catch_exceptions=False)
    cli_runner.invoke(cli.source.delete, ['test_mongo_antomation'], catch_exceptions=False)
