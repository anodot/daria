import click
import os

from datetime import datetime
from agent.modules.constants import AGENT_DB_USER, AGENT_DB, BACKUP_DIRECTORY, AGENT_DB_HOST
from agent import pipeline
from agent.modules.streamsets_api_client import api_client as streamsets_api_client


@click.command()
def backup():
    filename = os.path.join(BACKUP_DIRECTORY, f'{AGENT_DB}_{datetime.now():%Y-%m-%d_%H:%M:%S}.dump')
    if os.system(f'pg_dump -Fc -h {AGENT_DB_HOST} -U {AGENT_DB_USER} {AGENT_DB} > {filename}') == 0:
        click.secho(f'{AGENT_DB} database successfully dumped to {filename}', fg='green')


@click.command()
@click.argument('dump_file', type=click.Path(exists=True))
def restore(dump_file):
    if click.confirm(f'Are you sure you want to restore `{AGENT_DB}` database from the dump? All current data in the database will be overwritten'):
        if os.system(f'pg_restore -c -h {AGENT_DB_HOST} -U {AGENT_DB_USER} -d {AGENT_DB} {dump_file}') == 0:
            click.secho(f'Database {AGENT_DB} successfully restored', fg='green')
            _restore_pipelines()


def _restore_pipelines():
    existing, not_existing = _get_pipelines()
    for pipeline_ in existing:
        pipeline.manager.update(pipeline_)
    for pipeline_ in not_existing:
        pipeline.manager.create(pipeline_)


def _get_pipelines():
    streamsets_pipelines = [p['pipelineId'] for p in streamsets_api_client.get_pipelines()]
    existing = []
    not_existing = []
    for p in pipeline.repository.get_all():
        if p.name in streamsets_pipelines:
            existing.append(p)
        else:
            not_existing.append(p)
    return existing, not_existing
