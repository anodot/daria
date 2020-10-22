import os
import subprocess

from agent import cli


def test_antomation(cli_runner):
    dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'agent', 'scripts', 'antomation')
    script_path = os.path.join(dir_path, 'populate_sources_and_pipelines.py')
    checksums_path = os.path.join(dir_path, 'checksums')
    try:
        subprocess.check_output(['python', script_path], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        print("Status: FAIL", exc.returncode, exc.output)
        raise
    cli_runner.invoke(cli.pipeline.delete, ['test_mongo_pipeline_antomation'], catch_exceptions=False)
    cli_runner.invoke(cli.source.delete, ['test_mongo_antomation'], catch_exceptions=False)
    with open(os.path.join(checksums_path, 'pipelines.csv'), 'w') as f:
        f.write('')
    with open(os.path.join(checksums_path, 'sources.csv'), 'w') as f:
        f.write('')
