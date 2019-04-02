import click
import json
import os
import urllib.parse

from .pipeline.cli import pipeline, DESTINATION_FILE
from .source.cli import source


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
        "config": {},
        "type": "http"
    }
    if os.path.isfile(DESTINATION_FILE):
        if not click.confirm('Destination is already configured. Do you want to edit it?'):
            return

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

    with open(DESTINATION_FILE, 'w') as f:
        json.dump(dest, f)

    click.secho('Destination configured', fg='green')


agent.add_command(source)
agent.add_command(pipeline)
agent.add_command(destination)

if __name__ == '__main__':
    agent()
