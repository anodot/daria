import click
import os

from .pipeline.cli import pipeline, TOKEN_FILE
from .source.cli import source


@click.group()
def agent():
    pass


@click.command()
def token():
    """
    Add anodot API token
    You can copy it from Settings > API tokens > Data Collection in your anodot account
    """
    if os.path.isfile(TOKEN_FILE):
        if not click.confirm('Anodot token is already configures. Do you want to edit it?'):
            return

    with open(TOKEN_FILE, 'w') as f:
        f.write(click.prompt('Enter anodot api token', type=click.STRING))

    click.secho('Token configured', fg='green')


agent.add_command(source)
agent.add_command(pipeline)
agent.add_command(token)


if __name__ == '__main__':
    agent()
