import traceback
import click
import requests

from agent import streamsets
from agent.modules.logger import get_logger
from agent.streamsets import StreamSets
from agent.modules import constants, validator
from agent.modules.tools import infinite_retry

logger = get_logger(__name__, stdout=True)


def get_url_complete(ctx, args, incomplete):
    return [s.url for s in streamsets.repository.get_all() if incomplete in s.url]


@click.group(name='streamsets')
def streamsets_group():
    pass


@click.command(name='list')
def list_():
    for name in streamsets.repository.get_all_names():
        click.echo(name)


@click.command()
def add():
    streamsets.manager.create_streamsets(
        _prompt_streamsets(StreamSets('', '', '', ''))
    )


@click.command()
@click.argument('url', autocompletion=get_url_complete)
def edit(url):
    try:
        s = streamsets.repository.get_by_url(url)
    except streamsets.repository.StreamsetsNotExistsException as e:
        raise click.ClickException(str(e))
    streamsets_ = _prompt_streamsets(s)
    streamsets.repository.save(streamsets_)


@click.command()
@click.argument('url', autocompletion=get_url_complete)
def delete(url):
    try:
        streamsets.manager.delete_streamsets(
            streamsets.repository.get_by_url(url)
        )
    except (streamsets.repository.StreamsetsNotExistsException, streamsets.manager.StreamsetsException) as e:
        raise click.ClickException(str(e))
    click.echo(f'Streamsets `{url}` is successfully deleted from the agent')


@click.command()
def balance():
    streamsets_ = streamsets.repository.get_all()
    if len(streamsets_) == 1:
        logger.info(f'You have only one streamsets instance, can\'t balance')
        return
    elif len(streamsets_) == 0:
        logger.info(f'You don\'t have any streamsets instances, can\'t balance')
        return
    streamsets.manager.StreamsetsBalancer().balance()


def _prompt_streamsets(streamsets_: StreamSets) -> StreamSets:
    streamsets_.url = _prompt_url(streamsets_.url if streamsets_.url else None)
    streamsets_.username = click.prompt('Username', type=click.STRING, default=constants.DEFAULT_STREAMSETS_USERNAME)
    streamsets_.password = click.prompt('Password', type=click.STRING, default=constants.DEFAULT_STREAMSETS_PASSWORD)
    try:
        streamsets.validator.validate(streamsets_)
    except streamsets.validator.ValidationException as e:
        raise click.ClickException(str(e))
    streamsets_.agent_external_url = _prompt_agent_external_url()
    return streamsets_


@infinite_retry
def _prompt_url(default=None) -> str:
    url = click.prompt('Enter streamsets url', type=click.STRING, default=default)
    try:
        validator.validate_url_format_with_port(url)
    except validator.ValidationException as e:
        raise click.ClickException(str(e))
    try:
        res = requests.get(url)
        res.raise_for_status()
    except requests.exceptions.HTTPError:
        raise click.ClickException(f'Provided url returned {res.status_code} status code')
    except Exception as e:
        logger.debug(traceback.format_exc())
        raise click.ClickException(f'ERROR: {str(e)}')
    return url


@infinite_retry
def _prompt_agent_external_url() -> str:
    url = click.prompt('Agent external URL', constants.AGENT_DEFAULT_URL)
    try:
        validator.validate_url_format(url)
        streamsets.validator.validate_agent_external_url(url)
    except (validator.ValidationException, streamsets.validator.ValidationException) as e:
        raise click.ClickException(str(e))
    return url


streamsets_group.add_command(list_)
streamsets_group.add_command(add)
streamsets_group.add_command(edit)
streamsets_group.add_command(delete)
streamsets_group.add_command(balance)
