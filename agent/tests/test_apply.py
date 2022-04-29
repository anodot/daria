import os

from agent import cli, pipeline, source
from .conftest import INPUT_FILES_DIR


def test_apply_mongo(cli_runner):
    dir_path = os.path.join(INPUT_FILES_DIR, 'apply-config', 'mongo')
    result = cli_runner.invoke(cli.apply, args=['-d', dir_path], catch_exceptions=False)
    assert result.exit_code == 0


def test_apply_sage(cli_runner):
    dir_path = os.path.join(INPUT_FILES_DIR, 'apply-config', 'sage')
    result = cli_runner.invoke(cli.apply, args=['-d', dir_path], catch_exceptions=False)
    assert result.exit_code == 1
    result = cli_runner.invoke(cli.pipeline.list_pipelines, catch_exceptions=False)
    assert result.exit_code == 0
    assert 'test_sage_apply' in result.output
    assert 'test_sage_apply_exc' not in result.output


def teardown_module(module):
    pipeline.manager.delete_by_id('test_mongo_pipeline_apply')
    source.repository.delete_by_name('test_mongo_apply')
    pipeline.manager.delete_by_id('test_sage_apply')
    source.repository.delete_by_name('test_sage_apply')
