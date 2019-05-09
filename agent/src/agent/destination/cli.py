import click
from .http import HttpDestination


@click.command()
def destination():
    """
    Data destination config.
    Anodot API token - You can copy it from Settings > API tokens > Data Collection in your Anodot account
    Proxy for connecting to Anodot
    """
    dest = HttpDestination()

    conf = dest.config['config']

    token = click.prompt('Anodot api token', type=click.STRING)
    conf['conf.resourceUrl'] = dest.get_url(token)
    conf['conf.client.useProxy'] = click.confirm('Use proxy for connecting to Anodot?')
    if conf['conf.client.useProxy']:
        conf['conf.client.proxy.uri'] = click.prompt('Proxy uri', type=click.STRING,
                                                     default=conf.get('conf.client.proxy.uri'))
        conf['conf.client.proxy.username'] = click.prompt('Proxy username', type=click.STRING,
                                                          default=conf.get('conf.client.proxy.username', ''))
        conf['conf.client.proxy.password'] = click.prompt('Proxy password', type=click.STRING, default='')

    dest.save()

    click.secho('Destination configured', fg='green')
