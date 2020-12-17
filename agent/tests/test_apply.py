import os

from agent import cli, pipeline, source
from .conftest import INPUT_FILES_DIR


def test_apply(cli_runner):
    dir_path = os.path.join(INPUT_FILES_DIR, 'apply-config')
    result = cli_runner.invoke(cli.apply, args=['-d', dir_path], catch_exceptions=False)
    assert result.exit_code == 0


def teardown_module(module):
    pipeline.manager.delete_by_name('test_mongo_pipeline_apply')
    source.repository.delete_by_name('test_mongo_apply')
