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
        self.prompt_add_graph_name_dimension()
        self.prompt_static_dimensions()
        self.prompt_tags()
        self.set_transform()
        self.prompt_rename_dimensions()
        self.prompt_convert_into_bits()

    def prompt_step(self):
        self.config['step'] = \
            click.prompt('Step in seconds', type=click.INT, default=self.default_config.get('step'))

    def prompt_add_graph_name_dimension(self):
        self.config['add_graph_name_dimension'] = click.confirm('Add graph name as a dimension?')

    def prompt_convert_into_bits(self):
        self.config['convert_bytes_into_bits'] = click.confirm(
            'Convert bytes into bits where appropriate?',
            default=bool(self.default_config.get('convert_bytes_into_bits', False))
        )
