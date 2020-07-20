import os
import subprocess

from agent import cli
from .fixtures import cli_runner


def test_antomation(cli_runner):
    # if the script is not working the test will fail with an exception
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts', 'antomation', 'populate_sources_and_pipelines.py')
    process = subprocess.Popen(['python', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cli_runner.invoke(cli.pipeline.delete, ['test_mongo_pipeline_antomation'])
    cli_runner.invoke(cli.source.delete, ['test_mongo_antomation'])
