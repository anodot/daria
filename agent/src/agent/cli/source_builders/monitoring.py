
from .abstract_builder import Builder


class MonitoringSource(Builder):
    def prompt(self, default_config, advanced=False):
        pass

    def print_sample_data(self):
        pass

    def validate(self):
        pass
