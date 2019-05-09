import click
from .pipeline.cli import pipeline
from .source.cli import source
from .destination.cli import destination


@click.group()
def agent():
    pass


agent.add_command(source)
agent.add_command(pipeline)
agent.add_command(destination)

if __name__ == '__main__':
    agent()
