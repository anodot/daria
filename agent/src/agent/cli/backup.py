import click
import os

from datetime import datetime
from agent.modules.constants import AGENT_DB_USER, POSTGRES_DB, BACKUP_DIRECTORY


@click.command()
def backup():
    filename = os.path.join(BACKUP_DIRECTORY, f'{POSTGRES_DB}_{datetime.now():%Y-%m-%d_%H:%M:%S}.bak')
    os.system(f'pg_dump -h db -U {AGENT_DB_USER} {POSTGRES_DB} > {filename}')
    print(f'{POSTGRES_DB} database successfully dumped to {filename}')


@click.command()
@click.argument('dump_file')
def restore(dump_file):
    pass

# pg_dump -h db -U agent agent > /backup-data/agent.bak
