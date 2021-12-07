import os
import click

from jsonschema import ValidationError, SchemaError

from agent import pipeline, source
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
        raise e
    click.secho(f'Temporary Source {constants.LOCAL_RUN_TESTPIPELINE_NAME} added', fg='green')


def _add_pipeline():
    """
    Creates temporary pipeline for run-test-pipeline command
    """
    pipeline_file = os.path.join(constants.LOCAL_RUN_TESTPIPELINE_DIR, "pipelines", "test_pipeline.json")
    try:
        with open(pipeline_file, "r") as file:
            pipeline.json_builder.build_using_file(file)
    except (FileNotFoundError, ValidationError, pipeline.PipelineException) as e:
        raise e
    click.secho(f'Temporary Pipeline {constants.LOCAL_RUN_TESTPIPELINE_NAME} added', fg='green')


def _run_pipeline():
    # TODO
    # agent pipeline start PIPELINE_ID

    # TODO
    # agent pipeline info PIPELINE_ID
    pass


def perform_cleanup():
    """
    Perform deletion of temporary source and pipeline
    """
    # delete tmp pipeline
    if e := pipeline.manager.force_delete(constants.LOCAL_RUN_TESTPIPELINE_NAME):
        click.secho(f'Some exc occurred in pipeline deletion: {e}', fg='red')
    else:
        click.secho(f'Temporary Pipeline {constants.LOCAL_RUN_TESTPIPELINE_NAME} deleted', fg='green')

    # delete tmp source
    try:
        source.repository.delete_by_name(constants.LOCAL_RUN_TESTPIPELINE_NAME)
    except source.SourceException as e:
        click.secho(f'Some exc occurred in pipeline deletion: {e}', fg='red')
    else:
        click.secho(f'Temporary Source {constants.LOCAL_RUN_TESTPIPELINE_NAME} deleted', fg='green')
