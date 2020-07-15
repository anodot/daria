import click

from agent.pipeline.prompt import PromptConfig


class PromptConfigVictoria(PromptConfig):
    def prompt_config(self):
        self.prompt_metrics()
        self.prompt_shit()
        self.set_static_properties()
        self.set_tags()

    def prompt_metrics(self):
        # todo array? split by comma or space?
        self.config['metrics'] = click.prompt('query', type=click.STRING,
                                              default=self.default_config.get('metrics'))

    def prompt_shit(self):
        self.config['dimensions'] = click.prompt('Metric tags', type=click.STRING,
                                                 default=self.default_config.get('tags', 0))
