import click

from agent.cli.prompt.pipeline.schemaless import SchemalessPrompter


class CactiPrompter(SchemalessPrompter):
    def prompt_config(self):
        self.config['timestamp'] = {}
        self.config['timestamp']['type'] = 'unix'
        self.prompt_step()
        self.prompt_interval('Polling interval in seconds')
        self.prompt_days_to_backfill()
        self.prompt_delay()
        self.prompt_exclude_hosts()
        self.prompt_exclude_datasources()
        self.prompt_add_graph_name_dimension()
        self.prompt_static_dimensions()
        self.prompt_tags()
        self.set_transform()
        self.prompt_rename_dimensions()

    def prompt_step(self):
        self.config['step'] = \
            click.prompt('Step in seconds', type=click.INT, default=self.default_config.get('step'))

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

    def prompt_add_graph_name_dimension(self):
        self.config['add_graph_name_dimension'] = click.confirm('Add graph name as a dimension?')
