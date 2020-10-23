import click
import requests

from agent import destination, pipeline
from agent.modules.streamsets import StreamSets
from agent.modules import streamsets, constants
from agent.modules.streamsets.repository import StreamsetsNotExistsException
from agent.modules.tools import infinite_retry


@click.group(name='streamsets')
def streamsets_group():
    pass


@click.command()
def add():
    _prompt_streamsets(StreamSets('', '', ''))
    if destination.repository.exists():
        pipeline.manager.create_monitoring_pipelines()


# todo autocompletion
@click.command()
@click.argument('url')
def edit(url):
    try:
        s = streamsets.repository.get_by_url(url)
    except StreamsetsNotExistsException:
        raise click.UsageError(f'StreamSets with url {url} does not exist')
    _prompt_streamsets(s)


# todo autocompletion
@click.command()
@click.argument('url')
def delete(url):
    try:
        streamsets.repository.delete_by_url(url)
    except StreamsetsNotExistsException:
        raise click.UsageError(f'StreamSets with url {url} does not exist')


def _prompt_streamsets(streamsets_: StreamSets):
    streamsets_.url = _prompt_url()
    streamsets_.username = click.prompt('Username', type=click.STRING, default=constants.DEFAULT_STREAMSETS_USERNAME)
    streamsets_.password = click.prompt('Password', type=click.STRING, default=constants.DEFAULT_STREAMSETS_PASSWORD)
    streamsets.repository.save(streamsets_)


@infinite_retry
def _prompt_url():
    url = click.prompt('Enter streamsets url', type=click.STRING)
    status = requests.get(url).status_code
    if not status == 200:
        raise Exception(f'Provided url returned {status} status code')
    return url
