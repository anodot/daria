import json
import os
import traceback
import click
import requests
import sdc_client

from agent import streamsets, pipeline
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
@click.option('--url', type=click.STRING)
@click.option('--username', type=click.STRING, default='admin')
@click.option('--password', type=click.STRING, default='admin')
@click.option('--agent-ext-url', type=click.STRING, default='http://anodot-agent')
@click.option('--preferred-type', type=click.STRING, default=None)
def add(url, username, password, agent_ext_url, preferred_type):
    if url:
        _validate_streamsets_url(url)
        _validate_agent_external_url(agent_ext_url)
        streamsets_ = StreamSets(url, username, password, agent_ext_url, preferred_type)
        _validate_streamsets(streamsets_)
    else:
        streamsets_ = _prompt_streamsets(StreamSets(_prompt_url(), '', '', ''))
        streamsets_.agent_external_url = _prompt_agent_external_url(streamsets_)
    streamsets.manager.create_streamsets(streamsets_)
    click.secho('StreamSets instance added to the agent', fg='green')


@click.command()
@click.argument('url', autocompletion=get_url_complete)
@click.option('--update-pipelines/--no-update-pipelines', default=False)
def edit(url, update_pipelines=False):
    try:
        s = streamsets.repository.get_by_url(url)
    except streamsets.repository.StreamsetsNotExistsException as e:
        raise click.ClickException(str(e))
    streamsets_ = _prompt_streamsets(s)
    old_external_url = streamsets_.agent_external_url
    streamsets_.agent_external_url = _prompt_agent_external_url(streamsets_)
    streamsets.repository.save(streamsets_)
    if update_pipelines and old_external_url != streamsets_.agent_external_url:
        for pipeline_ in pipeline.repository.get_by_streamsets_id(streamsets_.id):
            sdc_client.update(pipeline_)
    click.secho('Changes saved', fg='green')


@click.command()
@click.argument('url', autocompletion=get_url_complete)
def delete(url):
    try:
        streamsets.manager.delete_streamsets(streamsets.repository.get_by_url(url))
    except (streamsets.repository.StreamsetsNotExistsException, streamsets.manager.StreamsetsException) as e:
        raise click.ClickException(str(e))
    click.secho(f'Streamsets `{url}` is deleted from the agent', fg='green')


@click.command()
@click.option('--asynchronous', '-a', is_flag=True, default=False, help="Asynchronous mode")
def balance(asynchronous):
    streamsets_ = streamsets.repository.get_all()
    if len(streamsets_) == 1:
        logger.info('You have only one streamsets instance, can\'t balance')
        return
    elif len(streamsets_) == 0:
        logger.info('You don\'t have any streamsets instances, can\'t balance')
        return
    try:
        if asynchronous and click.confirm('It is recommended to perform backup before asynchronous balancing. '
                                          'Are you sure you want to continue?'):
            sdc_client.StreamsetsBalancerAsync().balance()
        else:
            sdc_client.StreamsetsBalancer().balance()
        click.secho('Done', fg='green')
    except sdc_client.StreamsetsException as e:
        click.echo(str(e))
        click.echo('Use `agent pipeline restore` to rollback all pipelines')


@click.command()
@click.option('-d', '--dir-path', type=click.Path())
def export(dir_path):
    if not dir_path:
        dir_path = 'streamsets'
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

    if streamsets.repository.get_all():
        with open(os.path.join(dir_path, 'streamsets.json'), 'w+') as f:
            json.dump([ss.to_dict() for ss in streamsets.repository.get_all()], f)

    click.echo(f'All streamsets exported to the `{dir_path}` directory')


def _validate_streamsets(streamsets_: StreamSets):
    try:
        streamsets.validator.validate(streamsets_)
    except streamsets.validator.ValidationException as e:
        raise click.ClickException(str(e))


@infinite_retry
def _prompt_streamsets(streamsets_: StreamSets) -> StreamSets:
    streamsets_.username = click.prompt('Username', type=click.STRING, default=constants.DEFAULT_STREAMSETS_USERNAME)
    streamsets_.password = click.prompt('Password', type=click.STRING, default=constants.DEFAULT_STREAMSETS_PASSWORD)
    _validate_streamsets(streamsets_)
    return streamsets_


def _validate_streamsets_url(url):
    if streamsets.repository.exists(url):
        raise click.ClickException(f'StreamSets with URL `{url}` already exists')
    try:
        validator.validate_url_format_with_port(url)
    except validator.ValidationException as e:
        raise click.ClickException(str(e))
    try:
        res = requests.get(url)
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise click.ClickException(f'Provided url returned {e.response.status_code} status code')
    except Exception as e:
        logger.debug(traceback.format_exc())
        raise click.ClickException(f'ERROR: {e}')


@infinite_retry
def _prompt_url() -> str:
    url = click.prompt('Enter streamsets url', type=click.STRING)
    _validate_streamsets_url(url)
    return url


def _validate_agent_external_url(url):
    try:
        validator.validate_url_format(url)
    except (validator.ValidationException, streamsets.validator.ValidationException) as e:
        raise click.ClickException(str(e))


@infinite_retry
def _prompt_agent_external_url(streamsets_: StreamSets) -> str:
    default = streamsets_.agent_external_url or constants.AGENT_DEFAULT_URL
    url = click.prompt('Agent external URL', default)
    _validate_agent_external_url(url)
    return url


streamsets_group.add_command(list_)
streamsets_group.add_command(add)
streamsets_group.add_command(edit)
streamsets_group.add_command(delete)
streamsets_group.add_command(balance)
streamsets_group.add_command(export)
