import click
from .pipeline.cli import pipeline
from .source.cli import source
from .destination.cli import destination


@click.group()
def agent():
    pass


@click.command()
def upgrade():
    pass


agent.add_command(source)
agent.add_command(pipeline)
agent.add_command(destination)
agent.add_command(upgrade)

if __name__ == '__main__':
    agent()
