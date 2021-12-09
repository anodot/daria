import os
import time
import click
import sdc_client
from jsonschema import SchemaError, ValidationError

from agent import destination, pipeline, source
from agent.modules import constants
from agent.modules.logger import get_logger

logger = get_logger(__name__, stdout=True)


@click.command(name='run-test-pipeline')
def run_test_pipeline():
    """
    Test if everything works.
    """
    try:
        _check_prerequisites()
        _add_source()
        _add_pipeline()
        _run_pipeline()
    except Exception as e:
        click.secho(f'Test run failed: {e}', fg='red')
    else:
        click.secho('Test run OK', fg='green')
    finally:
        # clear after all stage
        perform_cleanup()


def _check_prerequisites():
    """
    Checks if streamsets and destination configured
    """
    if errors := pipeline.check_prerequisites():
        raise click.ClickException("\n".join(errors))


def _add_source():
    """
    Creates temporary source for run-test-pipeline command
    """
    source_file = os.path.join(constants.LOCAL_RUN_TESTPIPELINE_DIR, "sources", "test_source.json")
    try:
        with open(source_file, "r") as file:
            source.json_builder.create_from_file(file)
    except (ValidationError, SchemaError) as e:
        logger.error(e)
        raise Exception("Error during test Source creation. See error log for details")


def _add_pipeline():
    """
    Creates temporary pipeline for run-test-pipeline command
    """
    pipeline_file = os.path.join(constants.LOCAL_RUN_TESTPIPELINE_DIR, "pipelines", "test_pipeline.json")
    try:
        with open(pipeline_file, "r") as file:
            pipeline.json_builder.build_using_file(file)
    except (FileNotFoundError, ValidationError, pipeline.PipelineException) as e:
        logger.error(e)
        raise Exception("Error during test Pipeline creation. See error log for details")


def _run_pipeline():
    try:
        click.echo(f'Pipeline {constants.LOCAL_RUN_TESTPIPELINE_NAME} is starting...')
        pipeline.manager.start(pipeline.repository.get_by_id(constants.LOCAL_RUN_TESTPIPELINE_NAME))
        time.sleep(20)
        info_ = sdc_client.get_pipeline_info(pipeline.repository.get_by_id(constants.LOCAL_RUN_TESTPIPELINE_NAME), 10)
        info_status = info_["status"].split(" ", 1)[0]
        click.echo(
            f'Pipeline {constants.LOCAL_RUN_TESTPIPELINE_NAME} info: '
            f'status: {info_status} '
            f'metrics: {info_["metrics"]}'
        )
        if info_status != pipeline.Pipeline.STATUS_RUNNING:
            raise pipeline.PipelineException("Error in Pipeline running. See error log for details")
        sdc_client.stop(pipeline.repository.get_by_id(constants.LOCAL_RUN_TESTPIPELINE_NAME))
        click.echo(f'Pipeline {constants.LOCAL_RUN_TESTPIPELINE_NAME} is stopped')
    except (sdc_client.ApiClientException, pipeline.PipelineException) as e:
        raise e


def perform_cleanup():
    """
    Perform deletion of temporary source and pipeline
    """
    # delete temporary pipeline
    try:
        if e := pipeline.manager.force_delete(constants.LOCAL_RUN_TESTPIPELINE_NAME):
            raise pipeline.PipelineException(str(e))
    except (destination.repository.DestinationNotExists, pipeline.PipelineException):
        pass

    # delete temporary source
    try:
        source.repository.delete_by_name(constants.LOCAL_RUN_TESTPIPELINE_NAME)
    except (source.SourceException, source.repository.SourceNotExists):
        pass
