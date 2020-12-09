import json
import click

from agent import pipeline, source, streamsets
from agent import destination
from agent.modules.tools import infinite_retry
from jsonschema import ValidationError
from texttable import Texttable
from agent.cli import prompt


def get_pipelines_ids_complete(ctx, args, incomplete):
    return [p.name for p in pipeline.repository.get_all() if incomplete in p.name]


@click.command(name='list')
def list_pipelines():
    pipelines = pipeline.repository.get_all()
    statuses = streamsets.manager.get_all_pipeline_statuses()
    table = _build_table(['Name', 'Type', 'Status', 'Streamsets URL'],
                         [[p.name, p.source.type, statuses[p.name]['status'], p.streamsets.url] for p in pipelines])
    click.echo(table.draw())


@click.command()
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
def create(advanced, file):
    _check_destination()
    sources = source.repository.get_all_names()
    _check_sources(sources)

    _create_from_file(file) if file else _prompt(advanced, sources)


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
def edit(pipeline_id, advanced, file):
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')
    _edit_using_file(file) if file else _prompt_edit(advanced, pipeline_id)


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-f', '--file', type=click.File())
def start(pipeline_id, file):
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')

    pipeline_ids = [item['pipeline_id'] for item in pipeline.manager.extract_configs(file)] if file else [pipeline_id]

    for pipeline_id in pipeline_ids:
        try:
            click.echo(f'Pipeline {pipeline_id} is starting...')
            streamsets.manager.start(pipeline.repository.get_by_name(pipeline_id))
        except (streamsets.ApiClientException, pipeline.PipelineException) as e:
            click.secho(str(e), err=True, fg='red')
            continue


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-f', '--file', type=click.File())
def stop(pipeline_id, file):
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')

    pipeline_ids = [item['pipeline_id'] for item in pipeline.manager.extract_configs(file)] if file else [pipeline_id]

    for pipeline_id in pipeline_ids:
        try:
            streamsets.manager.stop(pipeline_id)
            click.secho(f'Pipeline {pipeline_id} is stopped', fg='green')
        except (streamsets.ApiClientException, pipeline.PipelineException) as e:
            click.secho(str(e), err=True, fg='red')
            continue


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def force_stop(pipeline_id):
    try:
        click.echo('Force pipeline stopping...')
        streamsets.manager.force_stop(pipeline_id)
        click.secho('Pipeline is stopped', fg='green')
    except (streamsets.ApiClientException, streamsets.PipelineException) as e:
        click.secho(str(e), err=True, fg='red')
        return


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-f', '--file', type=click.File())
def delete(pipeline_id, file):
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')

    pipeline_names = [item['pipeline_id'] for item in pipeline.manager.extract_configs(file)] if file else [pipeline_id]

    for pipeline_name in pipeline_names:
        try:
            pipeline.manager.delete_by_name(pipeline_name)
            click.echo(f'Pipeline {pipeline_name} deleted')
        except (
                streamsets.ApiClientException, pipeline.PipelineException, pipeline.repository.PipelineNotExistsException
        ) as e:
            click.secho(str(e), err=True, fg='red')
            continue


@click.command()
@click.argument('pipeline_name', autocompletion=get_pipelines_ids_complete)
def force_delete(pipeline_name):
    errors = pipeline.manager.force_delete(pipeline_name)
    for e in errors:
        click.secho(e, err=True, fg='red')
    click.echo('Finished')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('-l', '--lines', type=click.INT, default=10)
@click.option('-s', '--severity', type=click.Choice(['INFO', 'ERROR']), default=None)
def logs(pipeline_id, lines, severity):
    """
    Show pipeline logs
    """
    try:
        logs_ = streamsets.manager.get_pipeline_logs(pipeline_id, severity, lines)
    except streamsets.ApiClientException as e:
        raise click.ClickException(str(e))
    table = _build_table(['Timestamp', 'Severity', 'Category', 'Message'], logs_)
    click.echo(table.draw())


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


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('-l', '--lines', type=click.INT, default=10)
def info(pipeline_id, lines):
    """
    Show pipeline status, errors if any, statistics about amount of records sent
    """
    try:
        info_ = streamsets.manager.get_pipeline_info(pipeline_id, lines)
    except streamsets.ApiClientException as e:
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

    table = _build_table(['Timestamp', 'Status', 'Message', 'Records count'], info_['history'])
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
    except streamsets.ApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline offset reset')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
def update(pipeline_id):
    """
    Update all pipelines configuration, recreate and restart them
    """
    pipelines = [pipeline.repository.get_by_name(pipeline_id)] if pipeline_id else pipeline.repository.get_all()
    for p in pipelines:
        try:
            streamsets.manager.update(p)
            click.secho(f'Pipeline {p.name} updated', fg='green')
        except streamsets.manager.StreamsetsException as e:
            print(str(e))
            continue


@click.group(name='pipeline')
def pipeline_group():
    pass


def _create_from_file(file):
    try:
        pipeline.manager.create_from_json(json.load(file))
    except (streamsets.ApiClientException, ValidationError, pipeline.PipelineException) as e:
        raise click.ClickException(str(e))


def _prompt(advanced: bool, sources: list):
    source_name = click.prompt('Choose source config', type=click.Choice(sources), default=_get_default_source(sources))
    pipeline_id = _prompt_pipeline_id()

    pipeline_prompter = prompt.pipeline.get_prompter(pipeline.manager.create_object(pipeline_id, source_name))
    previous_config = _get_previous_pipeline_config(pipeline_prompter.pipeline.source.type)
    pipeline_prompter.prompt(previous_config, advanced)
    pipeline.manager.create(pipeline_prompter.pipeline)

    click.secho('Created pipeline {}'.format(pipeline_id), fg='green')
    if _should_prompt_preview(pipeline_prompter.pipeline):
        if click.confirm('Would you like to see the result data preview?', default=True):
            pipeline.manager.show_preview(pipeline_prompter.pipeline)
            print('To change the config use `agent pipeline edit`')


def _should_prompt_preview(pipeline_: pipeline.Pipeline) -> bool:
    return pipeline_.source.type not in [source.TYPE_VICTORIA]


def _edit_using_file(file):
    try:
        pipeline.manager.edit_using_file(file)
    except (pipeline.PipelineException, streamsets.manager.StreamsetsException) as e:
        raise click.UsageError(str(e))


def _prompt_edit(advanced, pipeline_id):
    try:
        pipeline_prompter = prompt.pipeline.get_prompter(pipeline.repository.get_by_name(pipeline_id))
        pipeline_prompter.prompt(pipeline_prompter.pipeline.to_dict(), advanced=advanced)
        streamsets.manager.update(pipeline_prompter.pipeline)
        pipeline.repository.save(pipeline_prompter.pipeline)

        click.secho('Updated pipeline {}'.format(pipeline_id), fg='green')
        if _should_prompt_preview(pipeline_prompter.pipeline):
            if click.confirm('Would you like to see the result data preview?', default=True):
                pipeline.manager.show_preview(pipeline_prompter.pipeline)
                print('To change the config use `agent pipeline edit`')
    except pipeline.repository.PipelineNotExistsException:
        raise click.UsageError(f'{pipeline_id} does not exist')


def _get_previous_pipeline_config(source_type: str) -> dict:
    pipelines_with_source = pipeline.repository.get_by_source(source_type)
    if pipelines_with_source:
        return max(pipelines_with_source, key=lambda p: p.last_edited).to_dict()
    return {}


@infinite_retry
def _prompt_pipeline_id():
    pipeline_id = click.prompt('Pipeline ID (must be unique)', type=click.STRING).strip()
    pipeline.manager.check_pipeline_id(pipeline_id)
    return pipeline_id


def _check_sources(sources):
    if len(sources) == 0:
        raise click.ClickException('No sources configs found. Use "agent source create"')


def _check_destination():
    if not destination.repository.exists():
        raise click.ClickException('Destination is not configured. Use "agent destination"')


def _get_default_source(sources):
    return sources[0] if len(sources) == 1 else None


def _build_table(header, rows):
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.header(header)
    table.set_header_align(['l' for _ in range(len(header))])

    max_widths = [len(i) for i in header]
    for row in rows:
        table.add_row(row)
        for idx, i in enumerate(row):
            max_widths[idx] = max(max_widths[idx], len(i))

    table.set_cols_width([min(i, 100) for i in max_widths])
    return table


pipeline_group.add_command(create)
pipeline_group.add_command(list_pipelines)
pipeline_group.add_command(start)
pipeline_group.add_command(stop)
pipeline_group.add_command(force_stop)
pipeline_group.add_command(delete)
pipeline_group.add_command(force_delete)
pipeline_group.add_command(logs)
pipeline_group.add_command(info)
pipeline_group.add_command(reset)
pipeline_group.add_command(edit)
pipeline_group.add_command(destination_logs)
pipeline_group.add_command(update)
