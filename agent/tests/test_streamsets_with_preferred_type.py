import json
import os
import pytest

from agent import cli, streamsets, pipeline, destination, source
from agent.cli.run_test_pipeline import _add_source
from agent.modules import constants
from .conftest import generate_input

# For this test, db must contain 2 streamsets
# If default streamsets(http://dc:18630) doesn't exists, it will be created, and deleted after
# 'http://dc2:18630' has preferred type 'directory'
# All 'directory' pipelines must be assigned to 'http://dc2:18630' and ignore 'http://dc:18630'

url = 'http://dc2:18630'
streamsets_to_create = [url]
try:
    streamsets.repository.get_by_url('http://dc:18630')
except streamsets.repository.StreamsetsNotExistsException:
    streamsets_to_create.append('http://dc:18630')


def test_streamsets(cli_runner):
    for streamsets_url in streamsets_to_create:
        args = ['--url', url]
        if streamsets_url == url:
            args.extend(['--preferred-type', 'directory'])
        print(args)
        result = cli_runner.invoke(cli.streamsets.add, args=args, catch_exceptions=True)
        streamsets.repository.get_by_url(streamsets_url)
        assert result.exit_code == 0


def test_edit_streamsets(cli_runner):
    input_ = {
        'username': '',
        'password': '',
        'agent_external_url': '',
    }
    result = cli_runner.invoke(cli.streamsets.edit, [url], catch_exceptions=False, input=generate_input(input_))
    streamsets.repository.get_by_url(url)
    assert result.exit_code == 0


def test_run_pipelines():
    with open(os.path.join(constants.TEST_RUN_CONFIGS_DIR, 'pipelines.json')) as f:
        test_config = json.load(f)[0]
    test_config_2 = test_config.copy()
    test_config_2['pipeline_id'] += '_1'
    _add_source()
    pipelines_ = pipeline.json_builder.build_multiple([test_config, test_config_2])
    assert len(pipelines_) == 2
    assert len(pipeline.repository.get_by_streamsets_url(url)) == 2
    perform_cleanup()


def test_delete_streamsets(cli_runner):
    for streamsets_url in streamsets_to_create:
        result = cli_runner.invoke(cli.streamsets.delete, [streamsets_url], catch_exceptions=False)
        with pytest.raises(streamsets.repository.StreamsetsNotExistsException):
            streamsets.repository.get_by_url(url)
        assert result.exit_code == 0


def perform_cleanup():
    try:
        pipeline.manager.force_delete(constants.TEST_RUN_PIPELINE_NAME)
    except (destination.repository.DestinationNotExists, pipeline.PipelineException):
        pass
    try:
        pipeline.manager.force_delete(constants.TEST_RUN_PIPELINE_NAME + '_1')
    except (destination.repository.DestinationNotExists, pipeline.PipelineException):
        pass
    try:
        source.repository.delete_by_name(constants.TEST_RUN_PIPELINE_NAME)
    except source.repository.SourceNotExists:
        pass
