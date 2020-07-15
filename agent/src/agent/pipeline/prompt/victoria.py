import click

from agent.pipeline.prompt import PromptConfig


class PromptConfigVictoria(PromptConfig):
    def prompt_config(self):
        self.prompt_query()
        self.prompt_start()
        self.prompt_end()
        self.set_static_properties()
        self.set_tags()

    def prompt_query(self):
        self.config['query'] = click.prompt('Query to export data from VictoriaMetrics', type=click.STRING,
                                            default=self.default_config.get('metrics'))

    def prompt_start(self):
        self.config['start'] = click.prompt('Start from timestamp', type=click.STRING,
                                            default=self.default_config.get('start'))

    def prompt_end(self):
        self.config['end'] = click.prompt('End timestamp', type=click.STRING, default=self.default_config.get('start'))
