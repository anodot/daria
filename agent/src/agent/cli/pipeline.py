import click
import json
import os
import sdc_client

from typing import Optional
from agent import pipeline, source, streamsets
from agent.modules.tools import infinite_retry
from jsonschema import ValidationError
from texttable import Texttable
from agent.cli import prompt, preview
from sdc_client import Severity
from agent.pipeline import Pipeline, check_raw_prerequisites


def get_pipelines_ids_complete(ctx, args, incomplete):
    return [p.name for p in pipeline.repository.get_all() if incomplete in p.name]


@click.command(name='list')
def list_pipelines():
    pipelines = pipeline.repository.get_all()
    statuses = sdc_client.get_all_pipeline_statuses()
    table = _build_table(
        ['Name', 'Type', 'Status', 'Streamsets URL'],
        [[p.name, p.source.type, statuses[p.name]['status'] if p.name in statuses else 'DOES NOT EXIST IN STREAMSETS', p.streamsets.url] for p in pipelines]
    )
    click.echo(table.draw())


@click.command()
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
def create(advanced: bool, file):
    _check_prerequisites()
    _create_from_file(file) if file else _prompt(advanced)


@click.command(name='create-raw')
@click.option('-f', '--file', type=click.File(), required=True)
def create_raw(file):
    _check_raw_prerequisites()
    try:
        pipeline.json_builder.build_multiple_raw(pipeline.json_builder.extract_configs(file))
    except (sdc_client.ApiClientException, ValidationError, pipeline.PipelineException) as e:
        raise click.ClickException(str(e))


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
def edit(pipeline_id: str, advanced: bool, file):
    _check_prerequisites()
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')
    _edit_using_file(file) if file else _prompt_edit(advanced, pipeline_id)


def _check_prerequisites():
    if errors := pipeline.check_prerequisites():
        raise click.ClickException("\n".join(errors))


def _check_raw_prerequisites():
    if errors := check_raw_prerequisites():
        raise click.ClickException("\n".join(errors))


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-f', '--file', type=click.File())
def start(pipeline_id: str, file):
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')

    pipeline_ids = [item['pipeline_id'] for item in pipeline.json_builder.extract_configs(file)] if file else [pipeline_id]

    for pipeline_id in pipeline_ids:
        try:
            click.echo(f'Pipeline {pipeline_id} is starting...')
            pipeline.manager.start(pipeline.repository.get_by_id(pipeline_id))
        except (sdc_client.ApiClientException, pipeline.PipelineException) as e:
            click.secho(str(e), err=True, fg='red')
            continue


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-f', '--file', type=click.File())
def stop(pipeline_id: str, file):
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')

    pipeline_ids = [item['pipeline_id'] for item in pipeline.json_builder.extract_configs(file)] if file else [pipeline_id]

    for pipeline_id in pipeline_ids:
        try:
            sdc_client.stop(pipeline.repository.get_by_id(pipeline_id))
            click.secho(f'Pipeline {pipeline_id} is stopped', fg='green')
        except (sdc_client.ApiClientException, pipeline.PipelineException) as e:
            click.secho(str(e), err=True, fg='red')
            continue


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def force_stop(pipeline_id: str):
    try:
        click.echo('Force pipeline stopping...')
        sdc_client.force_stop(pipeline.repository.get_by_id(pipeline_id))
        click.secho('Pipeline is stopped', fg='green')
    except sdc_client.ApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-f', '--file', type=click.File())
def delete(pipeline_id: str, file):
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')

    pipeline_ids = [item['pipeline_id'] for item in pipeline.json_builder.extract_configs(file)] if file else [pipeline_id]

    for pipeline_id in pipeline_ids:
        try:
            pipeline.manager.delete_by_id(pipeline_id)
            click.echo(f'Pipeline {pipeline_id} deleted')
        except (
            sdc_client.ApiClientException, pipeline.PipelineException, pipeline.repository.PipelineNotExistsException
        ) as e:
            click.secho(str(e), err=True, fg='red')
            continue


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def force_delete(pipeline_id: str):
    errors = pipeline.manager.force_delete(pipeline_id)
    for e in errors:
        click.secho(e, err=True, fg='red')
    click.echo('Finished')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('-l', '--lines', type=click.INT, default=10)
@click.option('-s', '--severity', type=click.Choice([Severity.INFO, Severity.ERROR]), default=None)
def logs(pipeline_id: str, lines: int, severity: Optional[Severity]):
    try:
        logs_ = sdc_client.get_pipeline_logs(pipeline.repository.get_by_id(pipeline_id), severity, lines)
    except sdc_client.ApiClientException as e:
        raise click.ClickException(str(e))
    table = _build_table(['Timestamp', 'Severity', 'Category', 'Message'], logs_)
    click.echo(table.draw())


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('--enable/--disable', default=False)
def destination_logs(pipeline_id: str, enable: bool):
    """
    Enable destination response logs for a pipeline (for debugging purposes only)
    """
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    if enable:
        pipeline.manager.enable_destination_logs(pipeline_)
    else:
        pipeline.manager.disable_destination_logs(pipeline_)
    click.secho('Updated pipeline {}'.format(pipeline_id), fg='green')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('-l', '--lines', type=click.INT, default=10)
def info(pipeline_id: str, lines: int):
    """
    Show pipeline status, errors if any, statistics about amount of records sent
    """
    try:
        info_ = sdc_client.get_pipeline_info(pipeline.repository.get_by_id(pipeline_id), lines)
    except sdc_client.ApiClientException as e:
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
def reset(pipeline_id: str):
    """
    Reset pipeline's offset
    """
    try:
        pipeline.manager.reset(pipeline.repository.get_by_id(pipeline_id))
    except sdc_client.ApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline offset reset')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
def update(pipeline_id: str):
    """
    Update all pipelines configuration, recreate and restart them
    """
    pipelines = [pipeline.repository.get_by_id(pipeline_id)] if pipeline_id else pipeline.repository.get_all()
    for p in pipelines:
        try:
            sdc_client.update(p)
            click.secho(f'Pipeline {p.name} updated', fg='green')
        except streamsets.manager.StreamsetsException as e:
            print(str(e))
            continue


@click.command()
@click.option('-d', '--dir-path', type=click.Path())
def export(dir_path):
    if not dir_path:
        dir_path = 'pipelines'
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

    for pipeline_ in pipeline.repository.get_all():
        with open(os.path.join(dir_path, pipeline_.name + '.json'), 'w+') as f:
            json.dump([pipeline_.export()], f)

    click.echo(f'All pipelines exported to the `{dir_path}` directory')


@click.group(name='pipeline')
def pipeline_group():
    pass


def _create_from_file(file):
    try:
        pipeline.json_builder.build_using_file(file)
    except (sdc_client.ApiClientException, ValidationError, pipeline.PipelineException) as e:
        raise click.ClickException(str(e))


def _prompt(advanced: bool):
    sources = source.repository.get_all_names()
    source_name = click.prompt('Choose source config', type=click.Choice(sources), default=_get_default_source(sources))
    pipeline_id = _prompt_pipeline_id()

    pipeline_ = pipeline.manager.create_object(pipeline_id, source_name)
    previous_pipeline_config = _get_previous_pipeline_config(pipeline_.source.type)

    pipeline_prompter = prompt.pipeline.get_prompter(pipeline_, previous_pipeline_config, advanced)
    pipeline_prompter.prompt()

    pipeline.manager.create(pipeline_prompter.pipeline)

    click.secho('Created pipeline {}'.format(pipeline_id), fg='green')
    _result_preview(pipeline_prompter.pipeline)


def _should_prompt_preview(pipeline_: Pipeline) -> bool:
    return pipeline_.source.type not in [source.TYPE_VICTORIA]


def _edit_using_file(file):
    try:
        pipeline.json_builder.edit_using_file(file)
    except (pipeline.PipelineException, streamsets.manager.StreamsetsException) as e:
        raise click.UsageError(str(e))


def _prompt_edit(advanced: bool, pipeline_id: str):
    try:
        pipeline_ = pipeline.repository.get_by_id(pipeline_id)
        pipeline_ = prompt.pipeline.get_prompter(pipeline_, pipeline_.config, advanced).prompt()
        pipeline.manager.update(pipeline_)
        _result_preview(pipeline_)
    except pipeline.repository.PipelineNotExistsException:
        raise click.UsageError(f'{pipeline_id} does not exist')


def _result_preview(pipeline_: Pipeline):
    if _should_prompt_preview(pipeline_):
        if click.confirm('Would you like to see the result data preview?', default=True):
            preview.show_preview(pipeline_)
            print('To change the config use `agent pipeline edit`')


def _get_previous_pipeline_config(source_type: str) -> dict:
    pipelines_with_source = pipeline.repository.get_by_source(source_type)
    if pipelines_with_source:
        return max(pipelines_with_source, key=lambda p: p.last_edited).config
    return {}


@infinite_retry
def _prompt_pipeline_id():
    pipeline_id = click.prompt('Pipeline ID (must be unique)', type=click.STRING).strip()
    pipeline.manager.check_pipeline_id(pipeline_id)
    return pipeline_id


def _get_default_source(sources: list):
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
pipeline_group.add_command(create_raw)
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
pipeline_group.add_command(export)
