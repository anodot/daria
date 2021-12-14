import json
import os
import time
import click
import sdc_client

from jsonschema.exceptions import ValidationError
from agent import cli, destination, pipeline, source
from agent.modules import constants
from agent.modules.logger import get_logger

logger = get_logger(__name__, stdout=True)


@click.command(name='run-test-pipeline')
@click.option('--no-delete', is_flag=True, help='Delete test Source and Pipeline.')
def run_test_pipeline(no_delete):
    """
    Creates temporary source and pipeline to check the destination is accessible.
    """
    try:
        cli.pipeline.check_prerequisites()
        _add_source()
        _add_pipeline()
        _run_pipeline()
    except click.ClickException as e:
        click.secho(f'Test run failed: {e}', fg='red')
        exit(1)
    else:
        click.secho('Test run completed', fg='green')
    finally:
        if not no_delete:
            perform_cleanup()


def _add_source():
    """
    Creates temporary source for run-test-pipeline command
    """
    if source.repository.exists(constants.LOCAL_RUN_TESTPIPELINE_NAME):
        return
    source_file = os.path.join(constants.LOCAL_RUN_TESTPIPELINE_DIR, "sources", "test_source.json")
    try:
        with open(source_file, "r") as file:
            source.json_builder.create_from_file(file)
    except (FileNotFoundError, ValidationError, source.SourceException):
        raise click.ClickException(f"Error during Source creation. See error log for details")


def _add_pipeline():
    """
    Creates temporary pipeline for run-test-pipeline command
    """
    if pipeline.repository.exists(constants.LOCAL_RUN_TESTPIPELINE_NAME):
        return
    pipeline_file = os.path.join(constants.LOCAL_RUN_TESTPIPELINE_DIR, "pipelines", "test_pipeline.json")
    try:
        with open(pipeline_file, "r") as file:
            pipeline.json_builder.build_using_file(file)
    except (FileNotFoundError, ValidationError, pipeline.PipelineException):
        raise click.ClickException(f"Error during Pipeline creation. See error log for details")


def _run_pipeline():
    """
    Runs the pipeline, get an info about delivery and stops pipeline
    """
    try:
        click.echo(f'Pipeline `{constants.LOCAL_RUN_TESTPIPELINE_NAME}` is starting...')
        pipeline_ = pipeline.repository.get_by_id(constants.LOCAL_RUN_TESTPIPELINE_NAME)
        pipeline.manager.start(pipeline_)
        time.sleep(20)
        cli.pipeline.get_info(constants.LOCAL_RUN_TESTPIPELINE_NAME, 10)
        sdc_client.stop(pipeline_)
        click.echo(f'Pipeline `{constants.LOCAL_RUN_TESTPIPELINE_NAME}` is stopped')
    except (sdc_client.ApiClientException, pipeline.PipelineException) as e:
        raise click.ClickException(e)


def perform_cleanup():
    """
    Performs deletion of temporary source and pipeline
    """
    try:
        pipeline.manager.force_delete(constants.LOCAL_RUN_TESTPIPELINE_NAME)
    except (destination.repository.DestinationNotExists, pipeline.PipelineException):
        pass

    try:
        source.repository.delete_by_name(constants.LOCAL_RUN_TESTPIPELINE_NAME)
    except source.repository.SourceNotExists:
        pass
