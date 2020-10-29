import click

from agent.pipeline.prompt import PromptConfig


class PromptConfigVictoria(PromptConfig):
    def prompt_config(self):
        self.prompt_query()
        self.prompt_aggregated_metric_name()
        self.prompt_days_to_backfill()
        self.prompt_interval()
        self.prompt_delay()
        self.config['timestamp'] = {}
        self.config['timestamp']['type'] = 'unix'
        self.set_static_properties()
        self.set_tags()

    def prompt_query(self):
        self.config['query'] = click.prompt('Query to export data from VictoriaMetrics', type=click.STRING,
                                            default=self.default_config.get('query'))

    def prompt_aggregated_metric_name(self):
        if self.advanced:
            self.config['aggregated_metric_name'] = \
                click.prompt('Aggregated metric name', type=click.STRING,
                             default=self.default_config.get('aggregated_metric_name'))
