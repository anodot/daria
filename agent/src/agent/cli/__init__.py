import os
import shutil
import click

from agent import di, source as source_m, pipeline as pipeline_m
from agent.cli.apply import apply
from agent.cli.backup import backup, restore
from agent.cli.destination import destination
from agent.cli.pipeline import pipeline_group
from agent.cli.source import source_group
from agent.cli.streamsets import streamsets_group
from agent.version import __version__, __build_time__, __git_sha1__


class DefaultHelp(click.Group):
    def __init__(self, *args, **kwargs):
        context_settings = kwargs.setdefault('context_settings', {})
        if 'help_option_names' not in context_settings:
            context_settings['help_option_names'] = ['-h', '--help']
        self.help_flag = context_settings['help_option_names'][0]
        super(DefaultHelp, self).__init__(*args, **kwargs)

    def parse_args(self, ctx, args):
        if not args:
            args = [self.help_flag]
        return super(DefaultHelp, self).parse_args(ctx, args)


@click.group(cls=DefaultHelp, invoke_without_command=True)
@click.option('-v', '--version', is_flag=True, default=False)
def agent(version):
    if version:
        click.echo('Daria Agent version ' + __version__)
        click.echo('Build Time (UTC): ' + __build_time__)
        click.echo('Git commit: ' + __git_sha1__)


@click.command()
def clean():
    if not click.confirm('You\'re going to DELETE ALL SOURCES AND PIPELINES, continue?'):
        return
    for pipeline_ in pipeline_m.repository.get_all():
        pipeline_m.manager.delete(pipeline_)
    for source_ in source_m.repository.get_all():
        source_m.manager.delete(source_)
    folder = '../../../output/'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def agent_entry_point():
    di.init()
    agent()


agent.add_command(clean)
agent.add_command(source_group)
agent.add_command(pipeline_group)
agent.add_command(backup)
agent.add_command(restore)
agent.add_command(destination)
agent.add_command(streamsets_group)
agent.add_command(apply)

if __name__ == '__main__':
    agent_entry_point()
