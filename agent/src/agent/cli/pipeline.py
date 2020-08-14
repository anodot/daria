import click

from agent import pipeline, source
from agent.pipeline import PipelineException
from agent.streamsets_api_client import api_client, StreamSetsApiClientException
from agent import destination
from agent.tools import infinite_retry
from jsonschema import ValidationError
from texttable import Texttable


def get_previous_pipeline_config(label):
    try:
        pipelines_with_source = api_client.get_pipelines(order_by='CREATED', order='DESC', label=label)
        if len(pipelines_with_source) > 0:
            pipeline_obj = pipeline.repository.get_by_name(pipelines_with_source[-1]['pipelineId'])
            return pipeline_obj.to_dict()
    except source.SourceConfigDeprecated:
        pass
    return {}


def build_table(header, data, get_row, *args):
    """
    :param header: list
    :param data: list
    :param get_row: function - accepts item as first argument and *args; return false if row is needed to be skipped
    :param args: list
    :return:
    """
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.header(header)
    table.set_header_align(['l' for i in range(len(header))])

    max_widths = [len(i) for i in header]
    for item in data:
        row = get_row(item, *args)
        if not row:
            continue
        table.add_row(row)
        for idx, i in enumerate(row):
            max_widths[idx] = max(max_widths[idx], len(i))

    table.set_cols_width([min(i, 100) for i in max_widths])
    return table


def get_pipelines_ids_complete(ctx, args, incomplete):
    return [p['pipelineId'] for p in api_client.get_pipelines() if incomplete in p['pipelineId']]


def create_from_file(file):
    try:
        pipeline.manager.create_from_file(file)
    except (StreamSetsApiClientException, ValidationError, PipelineException) as e:
        raise click.ClickException(str(e))


@click.command()
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
def create(advanced, file):
    check_destination()
    sources = source.repository.get_all_names()
    check_sources(sources)

    if file:
        create_from_file(file)
        return

    source_config_name = click.prompt('Choose source config', type=click.Choice(sources),
                                      default=get_default_source(sources))
    pipeline_id = prompt_pipeline_id()
    pipeline_manager = pipeline.manager.PipelineManager(pipeline.manager.create_object(pipeline_id, source_config_name))
    previous_config = get_previous_pipeline_config(pipeline_manager.pipeline.source.type)
    # the rest of the data is prompted in the .prompt() call
    pipeline_manager.prompt(previous_config, advanced)
    pipeline_manager.create()

    click.secho('Created pipeline {}'.format(pipeline_id), fg='green')

    if click.confirm('Would you like to see the result data preview?', default=True):
        pipeline_manager.show_preview()
        print('To change the config use `agent pipeline edit`')


@infinite_retry
def prompt_pipeline_id():
    pipeline_id = click.prompt('Pipeline ID (must be unique)', type=click.STRING).strip()
    pipeline.manager.check_pipeline_id(pipeline_id)
    return pipeline_id


def check_sources(sources):
    if len(sources) == 0:
        raise click.ClickException('No sources configs found. Use "agent source create"')


def check_destination():
    if not destination.repository.exists():
        raise click.ClickException('Destination is not configured. Use "agent destination"')


def get_default_source(sources):
    return sources[0] if len(sources) == 1 else None


def edit_using_file(file):
    try:
        pipeline.manager.edit_using_file(file)
    except PipelineException as e:
        raise click.UsageError(str(e))


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
def edit(pipeline_id, advanced, file):
    """
    Edit pipeline
    """
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')

    if file:
        edit_using_file(file)
        return

    try:
        pipeline_manager = pipeline.manager.PipelineManager(pipeline.repository.get_by_name(pipeline_id))
        pipeline_manager.prompt(pipeline_manager.pipeline.to_dict(), advanced=advanced)
        pipeline.manager.update(pipeline_manager.pipeline)

        click.secho('Updated pipeline {}'.format(pipeline_id), fg='green')
        if click.confirm('Would you like to see the result data preview?', default=True):
            pipeline_manager.show_preview()
            print('To change the config use `agent pipeline edit`')
    except pipeline.PipelineNotExistsException:
        raise click.UsageError(f'{pipeline_id} does not exist')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('--enable/--disable', default=False)
def destination_logs(pipeline_id, enable):
    """
    Enable destination response logs for a pipeline (for debugging purposes only)
    """
    pipeline_object = pipeline.repository.get_by_name(pipeline_id)
    pipeline.manager.enable_destination_logs(pipeline_object) if enable else pipeline.manager.disable_destination_logs(pipeline_object)
    click.secho('Updated pipeline {}'.format(pipeline_id), fg='green')


@click.command(name='list')
def list_pipelines():
    """
    List all pipelines
    """
    pipelines = api_client.get_pipelines()
    pipelines_status = api_client.get_pipelines_status()

    def get_row(item, statuses):
        return [item['title'], statuses[item['pipelineId']]['status'], item['pipelineId']]

    table = build_table(['Title', 'Status', 'ID'], pipelines, get_row, pipelines_status)

    click.echo(table.draw())


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-f', '--file', type=click.File())
def start(pipeline_id, file):
    """
    Start pipeline
    """

    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')

    pipeline_ids = [item['pipeline_id'] for item in pipeline.manager.extract_configs(file)] if file else [pipeline_id]

    for pipeline_id in pipeline_ids:
        try:
            p = pipeline.repository.get_by_name(pipeline_id)
            click.echo(f'Pipeline {pipeline_id} is starting...')
            pipeline.manager.start(p)
        except (StreamSetsApiClientException, pipeline.PipelineException) as e:
            click.secho(str(e), err=True, fg='red')
            continue


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-f', '--file', type=click.File())
def stop(pipeline_id, file):
    """
    Stop pipeline
    """

    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')

    pipeline_ids = [item['pipeline_id'] for item in pipeline.manager.extract_configs(file)] if file else [pipeline_id]

    for pipeline_id in pipeline_ids:
        try:
            pipeline.manager.stop_by_id(pipeline_id)
            click.secho(f'Pipeline {pipeline_id} is stopped', fg='green')
        except (StreamSetsApiClientException, pipeline.PipelineException) as e:
            click.secho(str(e), err=True, fg='red')
            continue


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def force_stop(pipeline_id):
    """
    Force stop pipeline
    """
    try:
        click.echo('Force pipeline stopping...')
        pipeline.manager.force_stop_pipeline(pipeline_id)
        click.secho('Pipeline is stopped', fg='green')
    except (StreamSetsApiClientException, pipeline.PipelineException) as e:
        click.secho(str(e), err=True, fg='red')
        return


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-f', '--file', type=click.File())
def delete(pipeline_id, file):
    """
    Delete pipeline
    """
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')

    pipeline_ids = [item['pipeline_id'] for item in pipeline.manager.extract_configs(file)] if file else [pipeline_id]

    for pipeline_id in pipeline_ids:
        try:
            pipeline.manager.delete(pipeline.repository.get_by_name(pipeline_id))
            click.echo(f'Pipeline {pipeline_id} deleted')
        except pipeline.PipelineNotExistsException:
            pipeline.manager.delete_by_id(pipeline_id)
            click.echo(f'Pipeline {pipeline_id} deleted')
        except (StreamSetsApiClientException, pipeline.PipelineException) as e:
            click.secho(str(e), err=True, fg='red')
            continue


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('-l', '--lines', type=click.INT, default=10)
@click.option('-s', '--severity', type=click.Choice(['INFO', 'ERROR']), default=None)
def logs(pipeline_id, lines, severity):
    """
    Show pipeline logs
    """
    try:
        logs_ = pipeline.info.get_logs(pipeline_id, severity, lines)
    except StreamSetsApiClientException as e:
        raise click.ClickException(str(e))
    table = build_table(['Timestamp', 'Severity', 'Category', 'Message'], logs_, lambda x: x)
    click.echo(table.draw())


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('-l', '--lines', type=click.INT, default=10)
def info(pipeline_id, lines):
    """
    Show pipeline status, errors if any, statistics about amount of records sent
    """
    try:
        info_ = pipeline.info.get(pipeline_id, lines)
    except StreamSetsApiClientException as e:
        raise click.ClickException(str(e))
    click.secho('=== STATUS ===', fg='green')
    click.echo(info_['status'])

    if info_['metrics']:
        click.echo('')
        click.echo(info_['metrics'])

    if info_['metric_errors']:
        click.echo('')
        click.secho('=== ERRORS ===', fg='red')
        for error in info_['metric_errors']:
            click.echo(error)

    if info_['pipeline_issues']:
        click.echo('')
        click.secho('=== ISSUES ===', bold=True, fg='red')
        for issue in info_['pipeline_issues']:
            click.echo(issue)

    if info_['stage_issues']:
        click.echo('')
        click.secho('=== STAGE ISSUES ===', bold=True, fg='red')
        for stage, issues in info_['stage_issues'].items():
            click.secho('Stage name: ' + stage, bold=True)
            for issue in issues:
                click.echo(issue)

    table = build_table(['Timestamp', 'Status', 'Message', 'Records count'], info_['history'], lambda x: x)
    click.echo('')
    click.secho('=== HISTORY ===', fg='green')
    click.echo(table.draw())


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def reset(pipeline_id):
    """
    Reset pipeline's offset
    """
    try:
        pipeline.manager.reset(pipeline.repository.get_by_name(pipeline_id))
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline offset reset')


@click.command()
def update():
    """
    Update all pipelines configuration, recreate and restart them
    """
    for p in pipeline.repository.get_all():
        try:
            pipeline.manager.update(p)
            click.secho(f'Pipeline {p.id} updated', fg='green')
        except pipeline.PipelineException as e:
            print(str(e))
            continue


@click.group(name='pipeline')
def pipeline_group():
    """
    Pipelines management
    """
    pass


pipeline_group.add_command(create)
pipeline_group.add_command(list_pipelines)
pipeline_group.add_command(start)
pipeline_group.add_command(stop)
pipeline_group.add_command(force_stop)
pipeline_group.add_command(delete)
pipeline_group.add_command(logs)
pipeline_group.add_command(info)
pipeline_group.add_command(reset)
pipeline_group.add_command(edit)
pipeline_group.add_command(destination_logs)
pipeline_group.add_command(update)
