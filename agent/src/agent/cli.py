import click

from .pipeline.cli import pipeline
from .destination.cli import destination
from .source.cli import source


@click.group()
def agent():
    pass


agent.add_command(source)
agent.add_command(destination)
agent.add_command(pipeline)
