import click
import time

from .pipeline import Pipeline
from .pipeline.cli import pipeline
from .source.cli import source
from .destination.cli import destination
from agent.streamsets_api_client import api_client, StreamSetsApiClientException


@click.group()
def agent():
    pass


@click.command()
def upgrade():

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
        pipeline_obj.update()

        if p['pipelineId'] in running_pipelines:
            api_client.start_pipeline(pipeline_obj.id)
        click.secho('Destination configured', fg='green')


agent.add_command(source)
agent.add_command(pipeline)
agent.add_command(destination)
agent.add_command(upgrade)

if __name__ == '__main__':
    agent()
