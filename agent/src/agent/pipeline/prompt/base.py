import click

from agent.cli.source_builders import get_builder
from agent.tools import infinite_retry, if_validation_enabled, dict_get_nested
from agent.pipeline import pipeline as p


class PromptConfig:
    timestamp_types = ['string', 'datetime', 'unix', 'unix_ms']

    def __init__(self, pipeline: p.Pipeline):
        self.advanced = False
        self.default_config = {}
        self.config = {}
        self.pipeline = pipeline

    def prompt(self, default_config, advanced=False):
        self.advanced = advanced
        self.default_config = default_config
        self.config = dict()
        self.prompt_config()
        return self.config

    def prompt_config(self):
        pass

    def set_timestamp(self):
        self.config['timestamp'] = self.default_config.get('timestamp', {})
        self.config['timestamp']['name'] = self.prompt_property('Timestamp property name',
                                                                self.config['timestamp'].get('name'))
        self.config['timestamp']['type'] = click.prompt('Timestamp property type',
                                                        type=click.Choice(self.timestamp_types),
                                                        default=self.config['timestamp'].get('type', 'unix'))

        if self.config['timestamp']['type'] == 'string':
            self.config['timestamp']['format'] = click.prompt('Timestamp format string', type=click.STRING,
                                                              default=self.config['timestamp'].get('format'))

    @infinite_retry
    def prompt_property(self, text: str, default_value) -> str:
        value = click.prompt(text, type=click.STRING, default=default_value)
        self.validate_properties_names([value], self.pipeline.source.sample_data)
        return value

    @infinite_retry
    def prompt_dimensions(self, text: str, default_value: list) -> list:
        dimensions = click.prompt(text, type=click.STRING, value_proc=lambda x: x.split(), default=default_value)
        self.validate_properties_names(dimensions, self.pipeline.source.sample_data)
        return dimensions

    def set_dimensions(self):
        self.config['dimensions'] = self.default_config.get('dimensions', {})
        self.config['dimensions']['required'] = self.prompt_dimensions('Required dimensions',
                                                                       self.config['dimensions'].get('required', []))
        self.config['dimensions']['optional'] = click.prompt('Optional dimensions', type=click.STRING,
                                                             value_proc=lambda x: x.split(),
                                                             default=self.config['dimensions'].get('optional', []))

    @infinite_retry
    def prompt_tags(self):
        self.config['tags'] = self.default_config.get('tags', {})

        properties_str = ''
        if self.config['tags']:
            properties_str = ' '.join([key + ':' + ','.join(val) for key, val in self.config['tags'].items()])

        self.config['tags'] = {}

        properties_str = click.prompt('Tags', type=click.STRING, default=properties_str)
        for i in properties_str.split():
            pair = i.split(':')
            if len(pair) != 2:
                raise click.UsageError('Wrong format, correct example - key:val key2:val2')

            self.config['tags'][pair[0]] = pair[1].split(',')

    @infinite_retry
    def prompt_object(self, property_name, prompt_text):
        self.config[property_name] = self.default_config.get(property_name, {})

        properties_str = ''
        if self.config[property_name]:
            properties_str = ' '.join([key + ':' + val for key, val in self.config[property_name].items()])

        self.config[property_name] = {}

        properties_str = click.prompt(prompt_text, type=click.STRING, default=properties_str)
        for i in properties_str.split():
            pair = i.split(':')
            if len(pair) != 2:
                raise click.UsageError('Wrong format, correct example - key:val key2:val2')

            self.config[property_name][pair[0]] = pair[1]

    def set_static_properties(self):
        if self.advanced:
            self.prompt_object('properties', 'Additional properties')

    def set_tags(self):
        if self.advanced:
            self.prompt_tags()

    def set_measurement_name(self):
        self.config['measurement_name'] = click.prompt('Measurement name', type=click.STRING,
                                                       default=self.default_config.get('measurement_name'))

    def set_target_type(self):
        self.config['target_type'] = click.prompt('Target type', type=click.Choice(['counter', 'gauge']),
                                                  default=self.default_config.get('target_type', 'gauge'))

    @if_validation_enabled
    def validate_properties_names(self, names, sample_data):
        if not sample_data:
            return
        errors = []
        for value in names:
            for record in sample_data:
                if not dict_get_nested(record, value.split('/')):
                    print(f'Property {value} is not present in a sample record')
                    errors.append(value)
                    break
        if errors and not click.confirm('Continue?'):
            raise click.UsageError('Try again')

    @if_validation_enabled
    def data_preview(self):
        if click.confirm('Would you like to see the data preview?', default=True):
            # todo this is a temporary solution, it requires a lot of refactoring
            builder = get_builder(self.pipeline.source.name, self.pipeline.source.type)
            builder.source = self.pipeline.source
            builder.print_sample_data()
