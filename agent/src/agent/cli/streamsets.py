import click
import requests

from typing import List
from agent import destination, pipeline, streamsets
from agent.streamsets import StreamSets
from agent.pipeline import Pipeline
from agent.modules import constants
from agent.modules.tools import infinite_retry


def get_url_complete(ctx, args, incomplete):
    return [s.url for s in streamsets.repository.get_all() if incomplete in s.url]


@click.group(name='streamsets')
def streamsets_group():
    pass


@click.command()
def add():
    _prompt_streamsets(StreamSets('', '', ''))
    if destination.repository.exists():
        pipeline.manager.create_monitoring_pipelines()


@click.command()
@click.argument('url', autocompletion=get_url_complete)
def edit(url):
    try:
        s = streamsets.repository.get_by_url(url)
    except streamsets.repository.StreamsetsNotExistsException:
        raise click.UsageError(f'StreamSets with url {url} does not exist')
    _prompt_streamsets(s)


@click.command()
@click.argument('url', autocompletion=get_url_complete)
def delete(url):
    try:
        streamsets_ = streamsets.repository.get_by_url(url)
        pipelines = pipeline.repository.get_by_streamsets(streamsets_)
        if _has_pipelines(pipelines):
            # -1 because we don't count Monitoring
            if click.confirm(f'Streamsets with url {streamsets_.url} contains {len(pipelines) - 1} pipelines, all these pipelines will be DELETED, continue?'):
                for pipeline_ in pipelines:
                    pipeline.repository.delete(pipeline_)
        streamsets.repository.delete(streamsets_)
    except streamsets.repository.StreamsetsNotExistsException:
        raise click.UsageError(f'StreamSets with url {url} does not exist')


def _has_pipelines(pipelines: List[Pipeline]) -> bool:
    if len(pipelines) > 1:
        return True
    if len(pipelines) == 1 and not pipeline.manager.is_monitoring(pipelines[0]):
        return True
    return False


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


streamsets_group.add_command(add)
streamsets_group.add_command(edit)
streamsets_group.add_command(delete)
