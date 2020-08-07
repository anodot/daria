import click

from agent.pipeline.prompt import PromptConfig


class PromptConfigVictoria(PromptConfig):
    def prompt_config(self):
        self.prompt_query()
        self.prompt_days_to_backfill()
        self.prompt_interval()
        self.config['timestamp'] = {}
        self.config['timestamp']['type'] = 'unix'
        self.set_static_properties()
        self.set_tags()

    def prompt_query(self):
        self.config['query'] = click.prompt('Query to export data from VictoriaMetrics', type=click.STRING,
                                            default=self.default_config.get('query'))

    def prompt_days_to_backfill(self):
        self.config['days_to_backfill'] = \
            click.prompt('Collect since (days ago)', type=click.INT,
                         default=self.default_config.get('days_to_backfill', 0))

    def prompt_interval(self):
        self.config['interval'] = click.prompt('Query interval (in seconds)', type=click.INT,
                                               default=self.default_config.get('interval'))
