import click

from agent.cli.prompt.pipeline import Prompter


class CactiPrompter(Prompter):
    def prompt_config(self):
        self.prompt_interval('Polling interval in seconds')
        self.prompt_exclude_hosts()
        self.prompt_exclude_datasources()
        self.set_static_dimensions()
        self.set_tags()

    def prompt_exclude_hosts(self):
        hosts = click.prompt(
            'List of hosts to exclude separated by comma (example: host1, host2)', type=click.STRING,
            default=','.join(self.default_config.get('exclude_hosts', []))
        )
        self.config['exclude_hosts'] = [host.strip() for host in hosts.split(',')]

    def prompt_exclude_datasources(self):
        ds = click.prompt(
            'List of data sources to exclude separated by comma (example: ds1, ds2)', type=click.STRING,
            default=','.join(self.default_config.get('exclude_datasources', []))
        )
        self.config['exclude_datasources'] = [host.strip() for host in ds.split(',')]
