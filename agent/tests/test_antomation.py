import os
import subprocess

from scripts.antomation.populate_sources_and_pipelines import ROOT_DIR
from agent import cli
from .fixtures import cli_runner


def test_antomation(cli_runner):
    # if the script is not working the test will fail with an exception
    path = os.path.join(ROOT_DIR, 'populate_sources_and_pipelines.py')
    process = subprocess.Popen(['python', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cli_runner.invoke(cli.pipeline.delete, ['test_mongo_pipeline_antomation'])
    cli_runner.invoke(cli.source.delete, ['test_mongo_antomation'])
