import click
import time

from .pipeline import Pipeline
from .pipeline.cli import pipeline
from .source.cli import source_group
from .destination.cli import destination
from agent.streamsets_api_client import api_client, StreamSetsApiClientException
from agent.version import __version__


@click.group(invoke_without_command=True)
@click.option('-v', '--version', is_flag=True, default=False)
def agent(version):
    click.echo('Daria Agent ' + __version__)


@click.command()
def update():

    running_pipelines = []
    for p in api_client.get_pipelines():
        try:
            api_client.stop_pipeline(p['pipelineId'])
        except StreamSetsApiClientException:
            continue
        running_pipelines.append(p['pipelineId'])

    time.sleep(3)
    for p in api_client.get_pipelines():
        pipeline_obj = Pipeline(p['pipelineId'])
        pipeline_obj.load()
        pipeline_obj.delete()
        pipeline_obj.create()

        if p['pipelineId'] in running_pipelines:
            api_client.start_pipeline(pipeline_obj.id)
        click.secho(f'Pipeline {p["pipelineId"]} updated', fg='green')


agent.add_command(source_group)
agent.add_command(pipeline)
agent.add_command(destination)
agent.add_command(update)

if __name__ == '__main__':
    agent()
