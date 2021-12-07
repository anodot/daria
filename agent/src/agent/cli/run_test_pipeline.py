import os
import click

from jsonschema import ValidationError, SchemaError

from agent import destination, pipeline, source, streamsets
from agent.modules import constants
from agent.modules.logger import get_logger

logger = get_logger(__name__, stdout=True)


@click.command(name='run-test-pipeline')
@click.option('--url', type=click.STRING, default=constants.ANODOT_API_URL)
@click.option('-t', '--token', type=click.STRING, default=None, required=True)
@click.option('--access-key', type=click.STRING, default=None)
def run_test_pipeline(url, token, access_key):
    """
    Test if everything works.
    """
    logger.info("run_test_pipeline CALL")
    logger.info(f"test_dir = {constants.LOCAL_RUN_TESTPIPELINE_DIR}")

    try:
        _add_streamset()
        _add_source()
        _add_destination(token, url, access_key)
        _add_pipeline()
        _run_pipeline()
    except Exception as e:
        raise click.ClickException(str(e))
    finally:
        # clear after all stage
        perform_cleanup()


def _add_streamset():
    """
    Creates temporary streamset for run-test-pipeline command
    """
    streamset_conf = {
        "url": constants.DEFAULT_STREAMSETS_URL,
        "username": constants.DEFAULT_STREAMSETS_USERNAME,
        "password": constants.DEFAULT_STREAMSETS_PASSWORD,
        "agent_external_url": constants.AGENT_DEFAULT_URL}

    streamsets_ = streamsets.StreamSets(**streamset_conf)
    try:
        streamsets.validator.validate(streamsets_)
    except streamsets.validator.ValidationException as e:
        raise e
    streamsets.manager.create_streamsets(streamsets_)
    click.secho('TMP StreamSets instance added to the agent', fg='green')


def _add_source():
    """
    Creates temporary source for run-test-pipeline command
    """
    source_file = os.path.join(constants.LOCAL_RUN_TESTPIPELINE_DIR, "sources", "test_source.json")
    print(f"source_file exists: {os.path.exists(source_file)}")
    try:
        with open(source_file, "r") as file:
            source.json_builder.create_from_file(file)
    except (ValidationError, SchemaError) as e:
        raise e
    click.secho('TMP Source added to the agent', fg='green')


def _add_destination(token, url, access_key):
    """
    Creates temporary destination for run-test-pipeline command
    """
    result = destination.manager.create(token, url, access_key)
    if result.is_err():
        raise click.ClickException(result.value)


def _add_pipeline():
    """
    Creates temporary pipeline for run-test-pipeline command
    """
    pipeline_file = os.path.join(constants.LOCAL_RUN_TESTPIPELINE_DIR, "pipelines", "test_pipeline.json")
    try:
        # logger.info(f"pipeline_file: {pipeline_file}")
        with open(pipeline_file, "r") as file:
            pipeline.json_builder.build_raw_using_file(file)
    except (FileNotFoundError, ValidationError, pipeline.PipelineException) as e:
        raise e
    click.secho('TMP PipeLine added to the agent', fg='green')


def _run_pipeline():
    # TODO
    # agent pipeline start PIPELINE_ID

    # TODO
    # agent pipeline info PIPELINE_ID
    pass


def perform_cleanup():
    # delete tmp pipeline
    pipeline.manager.force_delete(constants.LOCAL_RUN_TESTPIPELINE_NAME)
    click.echo(f'TMP Pipeline {constants.LOCAL_RUN_TESTPIPELINE_NAME} deleted')

    # delete tmp source
    source.repository.delete_by_name(constants.LOCAL_RUN_TESTPIPELINE_NAME)
    click.secho(f'TMP Source {constants.LOCAL_RUN_TESTPIPELINE_NAME} deleted', fg='green')

    # delete tmp streamset
    try:
        streamsets.manager.delete_streamsets(streamsets.repository.get_by_url(constants.DEFAULT_STREAMSETS_URL))
    except (streamsets.repository.StreamsetsNotExistsException, streamsets.manager.StreamsetsException) as e:
        pass
    click.secho(f'TMP Streamsets `{constants.DEFAULT_STREAMSETS_URL}` is deleted from the agent', fg='green')
