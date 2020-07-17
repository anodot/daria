import os
import subprocess

from scripts.antomation.populate_sources_and_pipelines import ROOT_DIR


def test_antomation():
    # if the script is not working the test will fail with an exception
    path = os.path.join(ROOT_DIR, 'populate_sources_and_pipelines.py')
    process = subprocess.Popen(['python', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
