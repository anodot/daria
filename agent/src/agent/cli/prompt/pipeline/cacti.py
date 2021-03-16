import click

from agent.cli.prompt.pipeline import Prompter


class CactiPrompter(Prompter):
    def prompt_config(self):
        self.config['timestamp'] = {}
        self.config['timestamp']['type'] = 'unix'
        self.prompt_interval('Polling interval in seconds')
        self.prompt_days_to_backfill()
        self.prompt_delay()
        self.prompt_exclude_hosts()
        self.prompt_exclude_datasources()
        self.set_static_dimensions()
        self.set_tags()

    def prompt_exclude_hosts(self):
        hosts = ','.join(self.default_config.get('exclude_hosts', []))
        if self.advanced:
            hosts = click.prompt(
                'List of hosts to exclude separated by comma, can be masked with * (example: testhost_*, host1)', type=click.STRING,
                default=hosts
            )
        self.config['exclude_hosts'] = [host.strip() for host in hosts.split(',')]

    def prompt_exclude_datasources(self):
        ds = ','.join(self.default_config.get('exclude_datasources', []))
        if self.advanced:
            ds = click.prompt(
                'List of data sources to exclude separated by comma, can be masked with * (example: testsource_*, datasource1)', type=click.STRING,
                default=ds
            )
        self.config['exclude_datasources'] = [source.strip() for source in ds.split(',')]
