import click

from agent.cli.prompt.pipeline import Prompter


class CactiPrompter(Prompter):
    def prompt_config(self):
        self.prompt_interval('Polling interval in seconds')
        # self.config['timestamp'] = {}
        # self.config['timestamp']['type'] = 'unix'
        self.set_static_dimensions()
        self.set_tags()

    def prompt_query(self):
        self.config['query'] = click.prompt('Query to export data from VictoriaMetrics', type=click.STRING,
                                            default=self.default_config.get('query'))
