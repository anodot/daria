import click
import os

from datetime import datetime
from agent.modules.constants import AGENT_DB_USER, AGENT_DB, BACKUP_DIRECTORY, AGENT_DB_HOST


@click.command()
def backup():
    filename = os.path.join(BACKUP_DIRECTORY, f'{AGENT_DB}_{datetime.now():%Y-%m-%d_%H:%M:%S}.dump')
    if os.system(f'pg_dump -Fc -h {AGENT_DB_HOST} -U {AGENT_DB_USER} {AGENT_DB} > {filename}') == 0:
        click.secho(f'{AGENT_DB} database successfully dumped to {filename}', fg='green')


@click.command()
@click.argument('dump_file')
def restore(dump_file):
    if not os.path.isfile(dump_file):
        click.secho(f'Cannot open {dump_file}, make sure you enter the correct path', err=True, fg='red')
        return
    if click.confirm(f'Are you sure you want to restore `{AGENT_DB}` database from the dump? All current data in the database will be overwritten'):
        if os.system(f'pg_restore -c -h {AGENT_DB_HOST} -U {AGENT_DB_USER} -d {AGENT_DB} {dump_file}') == 0:
            click.secho(f'Database {AGENT_DB} successfully restored', fg='green')
