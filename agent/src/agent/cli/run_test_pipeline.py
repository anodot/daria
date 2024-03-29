import os
import click

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
    if source.repository.exists(constants.TEST_RUN_PIPELINE_NAME):
        return
    source_file = os.path.join(constants.TEST_RUN_CONFIGS_DIR, 'sources.json')
    try:
        with open(source_file, 'r') as file:
            source.json_builder.create_from_file(file)
    except (FileNotFoundError, ValidationError, source.SourceException) as e:
        logger.error(str(e))
        raise click.ClickException('Error during Source creation. See error log for details')


def _add_pipeline():
    """
    Creates temporary pipeline for run-test-pipeline command
    """
    if pipeline.repository.exists(constants.TEST_RUN_PIPELINE_NAME):
        return
    pipeline_file = os.path.join(constants.TEST_RUN_CONFIGS_DIR, 'pipelines.json')
    try:
        with open(pipeline_file, 'r') as file:
            pipeline.json_builder.build_using_file(file)
    except (FileNotFoundError, ValidationError, pipeline.PipelineException):
        raise click.ClickException('Error during Pipeline creation. See error log for details')


def _run_pipeline():
    """
    Runs the pipeline, gets an info about delivery and stops pipeline
    """
    pipeline_ = pipeline.repository.get_by_id(constants.TEST_RUN_PIPELINE_NAME)
    try:
        pipeline.manager.start(pipeline_, True)
        info = pipeline.manager.get_info(pipeline_, 10)
        stat = pipeline.manager.get_metrics(pipeline_)
        cli.pipeline.print_info(info)
        pipeline.manager.stop(pipeline_)
        if stat.has_error():
            raise click.ClickException(f'Pipeline `{constants.TEST_RUN_PIPELINE_NAME}` has errors')
        if stat.has_undelivered():
            raise click.ClickException(f'Pipeline `{constants.TEST_RUN_PIPELINE_NAME}` has undelivered data')
    except pipeline.PipelineException as e:
        raise click.ClickException(str(e))


def perform_cleanup():
    """
    Performs deletion of temporary source and pipeline
    """
    try:
        pipeline.manager.force_delete(constants.TEST_RUN_PIPELINE_NAME)
    except (destination.repository.DestinationNotExists, pipeline.PipelineException):
        pass

    try:
        source.repository.delete_by_name(constants.TEST_RUN_PIPELINE_NAME)
    except source.repository.SourceNotExists:
        pass
