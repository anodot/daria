import click
import json
import os
import time
import urllib.parse
import uuid

from .pipeline.cli import pipeline, create_pipeline, edit_pipeline
from .pipeline.config_handlers.monitoring import MonitoringConfigHandler
from .source.cli import source
from .streamsets_api_client import api_client
from agent.constants import DESTINATION_FILE


HOST_ID_LENGTH = 10


def generate_host_id(length=10):
    return str(uuid.uuid4()).replace('-', '')[:length].upper()


@click.group()
def agent():
    pass


@click.command()
def destination():
    """
    Data destination config.
    Anodot API token - You can copy it from Settings > API tokens > Data Collection in your Anodot account
    Proxy for connecting to Anodot
    """
    dest = {
        'config': {},
        'type': 'http',
        'host_id': generate_host_id(HOST_ID_LENGTH)
    }
    edit = False
    if os.path.isfile(DESTINATION_FILE):
        if not click.confirm('Destination is already configured. Do you want to edit it?'):
            return
        edit = True
        with open(DESTINATION_FILE, 'r') as f:
            dest = json.load(f)

    token = click.prompt('Anodot api token', type=click.STRING)
    api_url = os.environ.get('ANODOT_API_URL', 'https://api.anodot.com')
    dest['config']['conf.resourceUrl'] = urllib.parse.urljoin(api_url,
                                                              f'api/v1/metrics?token={token}&protocol=anodot20')
    dest['config']['conf.client.useProxy'] = click.confirm('Use proxy for connecting to Anodot?')
    if dest['config']['conf.client.useProxy']:
        dest['config']['conf.client.proxy.uri'] = click.prompt('Proxy uri', type=click.STRING,
                                                               default=dest['config'].get('conf.client.proxy.uri'))
        dest['config']['conf.client.proxy.username'] = click.prompt('Proxy username', type=click.STRING,
                                                                    default=dest['config'].get('conf.client.proxy.username', ''))
        dest['config']['conf.client.proxy.password'] = click.prompt('Proxy password', type=click.STRING, default='')

    pipeline_config = {'destination': dest, 'pipeline_id': 'Monitoring'}

    if edit:
        base_config = api_client.get_pipeline('Monitoring')
        config_handler = MonitoringConfigHandler(pipeline_config, base_config)
        api_client.stop_pipeline(pipeline_config['pipeline_id'])
        time.sleep(3)
        edit_pipeline(config_handler, pipeline_config)
    else:
        config_handler = MonitoringConfigHandler(pipeline_config)
        create_pipeline(config_handler, pipeline_config)

    api_client.start_pipeline(pipeline_config['pipeline_id'])

    with open(DESTINATION_FILE, 'w') as f:
        json.dump(dest, f)

    click.secho('Destination configured', fg='green')


agent.add_command(source)
agent.add_command(pipeline)
agent.add_command(destination)

if __name__ == '__main__':
    agent()
