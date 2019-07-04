import click
import time

from .http import HttpDestination
from ..streamsets_api_client import api_client
from agent.pipeline import Pipeline


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

    dest.save()

    pipeline_monitoring = Pipeline('Monitoring')

    if pipeline_monitoring.exists():
        api_client.stop_pipeline(pipeline_monitoring.id)
        time.sleep(3)
        pipeline_monitoring.update()
    else:
        pipeline_monitoring.create()

    api_client.start_pipeline(pipeline_monitoring.id)

    click.secho('Destination configured', fg='green')
