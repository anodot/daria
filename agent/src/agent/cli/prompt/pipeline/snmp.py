import click

from .base import Prompter


class SNMPPrompter(Prompter):
    def prompt_config(self):
        self.prompt_mibs_file()
        self.prompt_interval()
        self.config['timestamp'] = {}
        self.config['timestamp']['type'] = 'unix'
        self.prompt_static_dimensions()
        self.prompt_tags()

    def prompt_mibs_file(self):
        self.config['mibs_file'] = click.prompt(
            'Path to a file with list of MIBs',
            type=click.STRING,
            default=self.default_config.get('mibs_file')
        )
        with open(self.config['mibs_file']) as f:
            self.config['mibs'] = f.readlines()
