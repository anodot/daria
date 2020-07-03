import click

from agent.cli import destination
from agent.cli import pipeline
from agent.cli import source
from agent.repository import pipeline_repository
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
        click.echo('Daria Agent version: ' + __version__)
        click.echo('Build Time (UTC): ' + __build_time__)
        click.echo('Git commit: ' + __git_sha1__)


@click.command()
def update():
    """
    Update all pipelines configuration, recreate and restart them
    """
    for p in pipeline_repository.get_all():
        try:
            pipeline.manager.update(p)
            click.secho(f'Pipeline {p.id} updated', fg='green')
        except pipeline.PipelineException as e:
            print(str(e))
            continue


agent.add_command(source.source_group)
agent.add_command(pipeline.pipeline_group)
agent.add_command(destination.destination)
agent.add_command(update)

if __name__ == '__main__':
    agent()
