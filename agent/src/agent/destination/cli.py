import click
import json
import os
import time

from .http import HttpDestination
from ..streamsets_api_client import api_client
from ..pipeline.cli import create_pipeline, edit_pipeline
from ..pipeline.config_handlers.monitoring import MonitoringConfigHandler
from agent.constants import PIPELINES_DIR


@click.command()
def destination():
    """
    Data destination config.
    Anodot API token - You can copy it from Settings > API tokens > Data Collection in your Anodot account
    Proxy for connecting to Anodot
    """
    dest = HttpDestination()
    if dest.exists():
        dest.load()

    dest.update_url(click.prompt('Anodot api token', type=click.STRING))

    use_proxy = click.confirm('Use proxy for connecting to Anodot?')
    if use_proxy:
        uri = click.prompt('Proxy uri', type=click.STRING, default=dest.get_proxy_url())
        username = click.prompt('Proxy username', type=click.STRING, default=dest.get_proxy_username() or '')
        password = click.prompt('Proxy password', type=click.STRING, default='')
        dest.set_proxy(use_proxy, uri, username, password)
    else:
        dest.set_proxy(use_proxy)

    if dest.exists():
        with open(os.path.join(PIPELINES_DIR, 'Monitoring' + '.json'), 'r') as f:
            pipeline_config = json.load(f)
        pipeline_config['destination'] = dest.config
        base_config = api_client.get_pipeline('Monitoring')
        config_handler = MonitoringConfigHandler(pipeline_config, base_config)
        api_client.stop_pipeline(pipeline_config['pipeline_id'])
        time.sleep(3)
        edit_pipeline(config_handler, pipeline_config)
    else:
        pipeline_config = {'destination': dest.config, 'pipeline_id': 'Monitoring',
                           'source': {'type': 'Monitoring', 'name': 'Monitoring', 'config': {}}}
        config_handler = MonitoringConfigHandler(pipeline_config)
        create_pipeline(config_handler, pipeline_config)

    with open(os.path.join(PIPELINES_DIR, pipeline_config['pipeline_id'] + '.json'), 'w') as f:
        json.dump(pipeline_config, f)

    api_client.start_pipeline(pipeline_config['pipeline_id'])

    dest.save()

    click.secho('Destination configured', fg='green')
