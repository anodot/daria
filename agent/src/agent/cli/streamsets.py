import click
import requests

from agent import destination, pipeline, streamsets
from agent.modules.logger import get_logger
from agent.streamsets import StreamSets
from agent.modules import constants, validator
from agent.modules.tools import infinite_retry

logger = get_logger(__name__, stdout=True)
# todo api


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
    except streamsets.repository.StreamsetsNotExistsException as e:
        raise click.ClickException(str(e))
    _prompt_streamsets(s)


@click.command()
@click.argument('url', autocompletion=get_url_complete)
def delete(url):
    try:
        streamsets_ = streamsets.repository.get_by_url(url)
        if _has_pipelines(streamsets_):
            if not _can_move_pipelines():
                raise click.ClickException('Cannot move pipelines to a different streamsets as only one streamsets instance exists, cannot delete streamsets that has pipelines')
            streamsets.manager.StreamsetsBalancer().unload_streamsets(streamsets_)
        pipeline.manager.delete_monitoring_pipeline(streamsets_)
        streamsets.repository.delete(streamsets_)
    except streamsets.repository.StreamsetsNotExistsException as e:
        raise click.ClickException(str(e))
    click.echo(f'Streamsets `{url}` is deleted from agent')


@click.command()
def balance():
    streamsets_ = streamsets.repository.get_all()
    if len(streamsets_) == 1:
        logger.info(f'You have only one streamsets instance, can\'t balance')
        return
    elif len(streamsets_) == 1:
        logger.info(f'You don\'t have any streamsets instances, can\'t balance')
        return
    streamsets.manager.StreamsetsBalancer().balance()


def _has_pipelines(streamsets_: StreamSets) -> bool:
    pipelines = pipeline.repository.get_by_streamsets_id(streamsets_.id)
    if len(pipelines) > 1:
        return True
    if len(pipelines) == 1 and not pipeline.manager.is_monitoring(pipelines[0]):
        return True
    return False


def _can_move_pipelines():
    return len(streamsets.repository.get_all()) > 1


def _prompt_streamsets(streamsets_: StreamSets):
    streamsets_.url = _prompt_url()
    streamsets_.username = click.prompt('Username', type=click.STRING, default=constants.DEFAULT_STREAMSETS_USERNAME)
    streamsets_.password = click.prompt('Password', type=click.STRING, default=constants.DEFAULT_STREAMSETS_PASSWORD)
    try:
        streamsets.StreamSetsApiClient(streamsets_).get_pipelines()
    except streamsets.UnauthorizedException:
        raise click.ClickException('Wrong username or password provided')
    except streamsets.ApiClientException as e:
        raise click.ClickException(str(e))
    streamsets.repository.save(streamsets_)


@infinite_retry
def _prompt_url() -> str:
    url = click.prompt('Enter streamsets url', type=click.STRING)
    if not validator.is_valid_url(url):
        raise click.ClickException('Wrong url format, please specify protocol and domain name')
    res = requests.get(url)
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError:
        raise click.ClickException(f'Provided url returned {res.status_code} status code')
    return url


streamsets_group.add_command(add)
streamsets_group.add_command(edit)
streamsets_group.add_command(delete)
streamsets_group.add_command(balance)
