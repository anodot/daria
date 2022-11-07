import click
import os
import sdc_client

from datetime import datetime
from agent.modules.constants import AGENT_DB_USER, AGENT_DB, BACKUP_DIRECTORY, AGENT_DB_HOST
from agent import pipeline
from agent.pipeline import Pipeline


@click.command()
def backup():
    """
    Backup the Database tables and StreamSets state.
    """
    filename = os.path.join(BACKUP_DIRECTORY, f'{AGENT_DB}_{datetime.now():%Y-%m-%d_%H:%M:%S}.dump')
    if os.system(f'pg_dump -Fc -h {AGENT_DB_HOST} -U {AGENT_DB_USER} {AGENT_DB} > {filename}') == 0:
        click.secho(f'{AGENT_DB} database successfully dumped to {filename}', fg='green')


@click.group()
def restore():
    """
    Restore DataBase and StreamSets commands.
    """
    pass


@restore.command()
@click.argument('dump_file', type=click.Path(exists=True))
def database(dump_file):
    """
    Restore DataBase tables.
    """
    if click.confirm(f'Are you sure you want to restore `{AGENT_DB}` database from the dump? All current data in the database will be overwritten'):
        if os.system(f'pg_restore -c -h {AGENT_DB_HOST} -U {AGENT_DB_USER} -d {AGENT_DB} {dump_file}') == 0:
            click.secho(f'Database `{AGENT_DB}` successfully restored', fg='green')


@restore.command()
@click.option('--use-available', is_flag=True, default=False)
def streamsets(use_available: bool):
    """
    Restore StreamSets states with its pipelines from DataBase.
    """
    _restore_pipelines(use_available)
    click.secho('StreamSets pipelines successfully restored', fg='green')


def _restore_pipelines(use_available):
    existing, not_existing = _get_pipelines()
    for pipeline_ in not_existing:
        click.echo(f'Creating pipeline `{pipeline_.name}`')
        if not sdc_client.get_pipeline_streamsets_stat(pipeline_):
            if use_available:
                pipeline_.set_streamsets(sdc_client.get_streamsets_for_pipeline(pipeline_))
            else:
                click.secho(f'StreamSets `{pipeline_.streamsets.get_url()}` not available', err=True, fg='red')
                continue
        pipeline.manager.create(pipeline_)
        _update_status(pipeline_)
        click.secho('Success', fg='green')
    for pipeline_ in existing:
        click.echo(f'Updating pipeline `{pipeline_.name}`')
        sdc_client.update(pipeline_)
        _update_status(pipeline_)
        click.secho('Success', fg='green')


def _get_pipelines():
    streamsets_pipelines = [p['pipelineId'] for p in sdc_client.get_all_pipelines()]
    existing = []
    not_existing = []
    for p in pipeline.repository.get_all():
        if p.name in streamsets_pipelines:
            existing.append(p)
        else:
            not_existing.append(p)
    return existing, not_existing


def _update_status(pipeline_: Pipeline):
    expected_status = pipeline_.status
    actual_status = sdc_client.get_pipeline_status(pipeline_)
    if expected_status in [Pipeline.STATUS_RUNNING, Pipeline.STATUS_STARTING]:
        if actual_status in [Pipeline.STATUS_EDITED, Pipeline.STATUS_STOPPED, Pipeline.STATUS_RUN_ERROR,
                             Pipeline.STATUS_STOP_ERROR, Pipeline.STATUS_START_ERROR]:
            pipeline.manager.start(pipeline_)
        elif actual_status == Pipeline.STATUS_STOPPING:
            sdc_client.force_stop(pipeline_)
            pipeline.manager.start(pipeline_)
    elif expected_status in [Pipeline.STATUS_EDITED, Pipeline.STATUS_STOPPED, Pipeline.STATUS_STOPPING]:
        if actual_status in [Pipeline.STATUS_RUNNING, Pipeline.STATUS_STARTING]:
            sdc_client.stop(pipeline_)
