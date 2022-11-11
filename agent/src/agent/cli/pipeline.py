import click
import json
import os
import sdc_client
import shutil

from pathlib import Path
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
    """
    List all available pipelines
    """
    pipelines = pipeline.repository.get_all()
    statuses = sdc_client.get_all_pipeline_statuses()
    table = _build_table(
        ['Name', 'Type', 'Status', 'Streamsets URL'],
        [
            [p.name, p.source.type, statuses[p.name]['status']
            if p.name in statuses
            else 'DOES NOT EXIST IN STREAMSETS', p.streamsets.url]
            for p in pipelines
        ]
    )
    click.echo(table.draw())


@click.command()
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
@click.option('-p', '--result-preview', is_flag=True)
def create(advanced: bool, file, result_preview: bool):
    """
    Create new Pipeline
    """
    check_prerequisites()
    try:
        _create_from_file(file, result_preview) if file else _prompt(advanced)
    except pipeline.PipelineException as e:
        raise click.ClickException(str(e)) from e


@click.command(name='create-raw')
@click.option('-f', '--file', type=click.File(), required=True)
def create_raw(file):
    """
    Create raw Pipeline
    """
    _check_raw_prerequisites()
    try:
        pipeline.json_builder.build_raw_using_file(file)
    except (sdc_client.ApiClientException, ValidationError, json.JSONDecodeError, pipeline.PipelineException) as e:
        raise click.ClickException(str(e))


@click.command(name='create-events')
@click.option('-f', '--file', type=click.File(), required=True)
def create_events(file):
    check_prerequisites()
    try:
        pipeline.json_builder.build_events_using_file(file)
    except (sdc_client.ApiClientException, ValidationError, pipeline.PipelineException) as e:
        raise click.ClickException(str(e)) from e


@click.command(name='create-topology')
@click.option('-f', '--file', type=click.File(), required=True)
def create_topology(file):
    check_prerequisites()
    try:
        pipeline.json_builder.build_topology_using_file(file)
    except (sdc_client.ApiClientException, ValidationError, pipeline.PipelineException) as e:
        raise click.ClickException(str(e)) from e


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
@click.option('-p', '--result-preview', is_flag=True)
def edit(pipeline_id: str, advanced: bool, file, result_preview: bool):
    """
    Edit config of an existing Pipeline
    """
    check_prerequisites()
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')
    _edit_using_file(file, result_preview) if file else _prompt_edit(advanced, pipeline_id)


def check_prerequisites():
    if errors := pipeline.check_prerequisites():
        raise click.ClickException("\n".join(errors))


def _check_raw_prerequisites():
    if errors := check_raw_prerequisites():
        raise click.ClickException("\n".join(errors))


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-f', '--file', type=click.File())
def start(pipeline_id: str, file):
    """
    Start a Pipelines to perform data collection
    """
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')
    for pipeline_id in _get_pipeline_ids(pipeline_id, file):
        try:
            click.echo(f'Pipeline {pipeline_id} is starting...')
            pipeline.manager.start(pipeline.repository.get_by_id(pipeline_id))
        except (
            sdc_client.ApiClientException, pipeline.PipelineException, pipeline.repository.PipelineNotExistsException
        ) as e:
            click.secho(str(e), err=True, fg='red')
            continue


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-f', '--file', type=click.File())
def stop(pipeline_id: str, file):
    """
    Stop a Pipelines to stop processing data
    """
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')
    for pipeline_id in _get_pipeline_ids(pipeline_id, file):
        try:
            sdc_client.stop(pipeline.repository.get_by_id(pipeline_id))
            click.secho(f'Pipeline {pipeline_id} is stopped', fg='green')
        except (
            sdc_client.ApiClientException, pipeline.PipelineException, pipeline.repository.PipelineNotExistsException
        ) as e:
            click.secho(str(e), err=True, fg='red')
            continue


def _get_pipeline_ids(pipeline_id, file):
    return [item['pipeline_id'] for item in pipeline.json_builder.extract_configs(file)] if file else [pipeline_id]


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def force_stop(pipeline_id: str):
    """
    Forcing a Pipeline to stop (often stops processes before they complete, which can lead to unexpected results)
    """
    try:
        click.echo('Force pipeline stopping...')
        sdc_client.force_stop(pipeline.repository.get_by_id(pipeline_id))
        click.secho('Pipeline is stopped', fg='green')
    except (sdc_client.ApiClientException, pipeline.repository.PipelineNotExistsException) as e:
        click.secho(str(e), err=True, fg='red')
        return


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-f', '--file', type=click.File())
@click.option('--delete-metrics', is_flag=True)
def delete(pipeline_id: str, file, delete_metrics: bool):
    """
    Delete a Pipeline by its name (safely stopping before deletion)
    """
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')
    for pipeline_id in _get_pipeline_ids(pipeline_id, file):
        try:
            pipeline.manager.delete_by_id(pipeline_id, delete_metrics=delete_metrics)
            click.echo(f'Pipeline {pipeline_id} deleted')
        except (
                sdc_client.ApiClientException, pipeline.PipelineException,
                pipeline.repository.PipelineNotExistsException
        ) as e:
            click.secho(str(e), err=True, fg='red')
            continue


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('--delete-metrics', is_flag=True)
def force_delete(pipeline_id: str, delete_metrics: bool):
    """
    Forcing to delete a Pipeline
    """
    errors = pipeline.manager.force_delete(pipeline_id, delete_metrics=delete_metrics)
    if errors:
        for e in errors:
            click.secho(e, err=True, fg='red')
    else:
        click.echo('Finished')


# todo severity is not working
@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('-l', '--lines', type=click.INT, default=10)
@click.option('-s', '--severity', type=click.Choice([Severity.INFO.value, Severity.ERROR.value]), default=None)
def logs(pipeline_id: str, lines: int, severity: Optional[Severity]):
    """
    Show a Pipeline logs
    """
    try:
        logs_ = sdc_client.get_pipeline_logs(pipeline.repository.get_by_id(pipeline_id), severity, lines)
    except (sdc_client.ApiClientException, pipeline.repository.PipelineNotExistsException) as e:
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
    try:
        pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    except pipeline.repository.PipelineNotExistsException as e:
        raise click.ClickException(str(e))
    if enable:
        pipeline.manager.enable_destination_logs(pipeline_)
    else:
        pipeline.manager.disable_destination_logs(pipeline_)
    click.secho(f'Updated pipeline {pipeline_id}', fg='green')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('-l', '--lines', type=click.INT, default=10)
def info(pipeline_id: str, lines: int):
    """
    Show pipeline status, errors if any, statistics about amount of records sent
    """
    try:
        pipeline_ = pipeline.repository.get_by_id(pipeline_id)
        info_ = pipeline.manager.get_info(pipeline_, lines)
        print_info(info_)
    except (sdc_client.ApiClientException, pipeline.repository.PipelineNotExistsException) as e:
        raise click.ClickException(str(e))


def print_info(info_: dict):
    """
    Prints out to console pipeline status, errors if any, statistics about amount of records sent
    """
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
            click.secho(f'Stage name: {stage}', bold=True)
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
    except (sdc_client.ApiClientException, pipeline.repository.PipelineNotExistsException) as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline offset reset')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('--asynchronous', '-a', is_flag=True, default=False, help="Asynchronous mode")
def update(pipeline_id: str, asynchronous: bool):
    """
    Update all pipelines configuration, recreate and restart them
    """
    pipelines = [pipeline.repository.get_by_id(pipeline_id)] if pipeline_id else pipeline.repository.get_all()
    if asynchronous:
        try:
            if click.confirm('It is recommended to perform backup before asynchronous update.'
                             'Are you sure you want to continue?'):
                sdc_client.update_async(pipelines)
                click.secho('Pipelines update finished', fg='green')
        except sdc_client.StreamsetsException as e:
            click.echo(str(e))
            click.echo('Use `agent pipeline restore` to rollback all pipelines')
    else:
        for p in pipelines:
            try:
                sdc_client.update(p)
                click.secho(f'Pipeline {p.name} updated', fg='green')
            except streamsets.manager.StreamsetsException as e:
                click.echo(str(e))
                continue


@click.command()
@click.option('-d', '--dir-path', type=click.Path())
def export(dir_path):
    """
    Export pipelines' config into file
    """

    def _export_config_to_file(path, config):
        if os.path.exists(path):
            return
        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, 'w+') as file_:
            file_.write(config)

    if not dir_path:
        dir_path = 'pipelines'
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

    for pipeline_ in pipeline.repository.get_all():
        pipeline_config = pipeline_.export()
        if pipeline_config.get('transform', {}).get('file'):
            _export_config_to_file(
                pipeline_config['transform']['file'],
                pipeline_config['transform']['config']
            )
        if pipeline_config.get('transform_script', {}).get('file'):
            _export_config_to_file(
                pipeline_config['transform_script']['file'],
                pipeline_config['transform_script']['config']
            )
        if pipeline_config.get('query_file'):
            _export_config_to_file(
                pipeline_config['query_file'],
                pipeline_config['query']
            )
        with open(os.path.join(dir_path, f'{pipeline_.name}.json'), 'w+') as f:
            json.dump([pipeline_.export()], f, indent=4)

    click.echo(f'All pipelines exported to the `{dir_path}` directory')


@click.group(name='pipeline')
def pipeline_group():
    pass


def _create_from_file(file, result_preview: bool):
    try:
        pipelines = pipeline.json_builder.build_using_file(file)
        if result_preview:
            for pipeline_ in pipelines:
                _result_preview(pipeline_)
    except (sdc_client.ApiClientException, ValidationError, json.JSONDecodeError, pipeline.PipelineException) as e:
        raise click.ClickException(str(e))


def _prompt(advanced: bool):
    sources = source.repository.get_all_names()
    source_name = click.prompt('Choose source config', type=click.Choice(sources), default=_get_default_source(sources))
    pipeline_id = _prompt_pipeline_id()

    pipeline_ = pipeline.manager.create_pipeline(pipeline_id, source_name)
    previous_pipeline_config = _get_previous_pipeline_config(pipeline_.source.type)

    pipeline_prompter = prompt.pipeline.get_prompter(pipeline_, previous_pipeline_config, advanced)
    pipeline_prompter.prompt()

    pipeline.manager.create(pipeline_prompter.pipeline)

    click.secho(f'Created pipeline {pipeline_id}', fg='green')
    _result_preview(pipeline_prompter.pipeline)


def _should_prompt_preview(pipeline_: Pipeline) -> bool:
    return pipeline_.source.type not in [source.TYPE_VICTORIA]


def _edit_using_file(file, result_preview: bool):
    try:
        pipelines = pipeline.json_builder.edit_using_file(file)
        if result_preview:
            for pipeline_ in pipelines:
                _result_preview(pipeline_)
    except (pipeline.PipelineException, streamsets.manager.StreamsetsException) as e:
        raise click.UsageError(str(e)) from e


def _prompt_edit(advanced: bool, pipeline_id: str):
    try:
        pipeline_ = pipeline.repository.get_by_id(pipeline_id)
        pipeline_ = prompt.pipeline.get_prompter(pipeline_, pipeline_.config, advanced).prompt()
        pipeline.manager.update(pipeline_)
        _result_preview(pipeline_)
    except pipeline.repository.PipelineNotExistsException as e:
        raise click.UsageError(f'{pipeline_id} does not exist') from e


def _result_preview(pipeline_: Pipeline):
    if (
        _should_prompt_preview(pipeline_)
        and click.confirm(f'Would you like to see the result data preview for `{pipeline_.name}`?', default=True)
    ):
        preview.show_preview(pipeline_)
        click.echo('To change the config use `agent pipeline edit`')


def _get_previous_pipeline_config(source_type: str) -> dict:
    if pipelines_with_source := pipeline.repository.get_by_source(source_type):
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
pipeline_group.add_command(create_events)
pipeline_group.add_command(create_topology)
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
