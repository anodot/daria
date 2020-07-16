import click

from agent.pipeline.prompt import PromptConfig


class PromptConfigVictoria(PromptConfig):
    def prompt_config(self):
        # todo базовая авторизация
        self.prompt_query()
        self.prompt_days_to_backfill()
        self.prompt_interval()
        self.set_static_properties()
        self.set_tags()

    def prompt_query(self):
        self.config['query'] = click.prompt('Query to export data from VictoriaMetrics', type=click.STRING,
                                            default=self.default_config.get('metrics'))

    def prompt_days_to_backfill(self):
        # что если дефолтного нет?
        self.config['days_to_backfill'] = \
            int(click.prompt('Collect since (days ago, collect all if empty)', type=click.STRING,
                             default=self.default_config.get('days_to_backfill')))

    def prompt_interval(self):
        self.config['query_interval_sec'] = click.prompt('Query interval (in seconds)', type=click.INT,
                                                         default=self.default_config.get('initial_offset'))
