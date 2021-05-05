import click

from agent.cli.prompt.pipeline.schemaless import SchemalessPrompter


class SolarWindsPrompter(SchemalessPrompter):
    def prompt_config(self):
        self.prompt_query()
        self.prompt_delay()
        self.prompt_days_to_backfill()
        self.prompt_interval()
        self.prompt_timestamp()
        # todo we don't need to as is static, values array path in set_values, split that function
        self.set_values()
        self.prompt_measurement_names()
        self.set_dimensions()
        self.prompt_static_dimensions()
        self.prompt_tags()

    def prompt_query(self):
        self.config['query'] = click.prompt(
            'Query to export data from SolarWinds',
            type=click.STRING,
            default=self.default_config.get('query')
        )
