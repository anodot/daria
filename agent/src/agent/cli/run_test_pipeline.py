import json
import os
import click

from agent import source, streamsets
from agent.modules import constants
from agent.modules.logger import get_logger
# from agent.streamsets import StreamSets

logger = get_logger(__name__, stdout=True)


# @click.argument('test_dir', envvar='RUN_TESTPIPELINE_DIR', type=click.Path(exists=True))
@click.command(name='run-test-pipeline')
def run_test_pipeline():
    """
    Test if everything works.
    """
    logger.info("run_test_pipeline CALL")
    logger.info(f"test_dir = {constants.LOCAL_RUN_TESTPIPELINE_DIR}")

    # TODO
    # agent streamsets add
    streamset_conf = {
        "url": constants.DEFAULT_STREAMSETS_URL,
        "username": constants.DEFAULT_STREAMSETS_USERNAME,
        "password": constants.DEFAULT_STREAMSETS_PASSWORD,
        "agent_external_url": constants.AGENT_DEFAULT_URL}

    streamsets_ = streamsets.StreamSets(**streamset_conf)
    try:
        streamsets.validator.validate(streamsets_)
    except streamsets.validator.ValidationException as e:
        raise click.ClickException(str(e))
    streamsets.manager.create_streamsets(streamsets_)
    click.secho('TMP StreamSets instance added to the agent', fg='green')

    # TODO
    # agent source create -f /path/to/source/config.json
    source_file = os.path.join(constants.LOCAL_RUN_TESTPIPELINE_DIR, "sources", "test_source.json")
    print(f"source_file exists: {os.path.exists(source_file)}")
    with open(source_file, "r") as file:
        source.json_builder.create_from_file(file)
    click.secho('TMP StreamSets instance added to the agent', fg='green')

    # TODO
    # agent pipeline create -f /path/to/pipeline/config.json
    pipeline_file = os.path.join(constants.LOCAL_RUN_TESTPIPELINE_DIR, "pipelines", "test_pipeline.json")
    print(f"pipeline_file exists: {os.path.exists(pipeline_file)}")

    # TODO
    # agent pipeline start PIPELINE_ID

    # TODO
    # agent pipeline info PIPELINE_ID

    # TODO
    # clear after all stages
