import click
import pytz

from agent.cli import preview
from agent.modules.tools import infinite_retry, if_validation_enabled, dict_get_nested
from agent import pipeline
from agent.pipeline import Pipeline


class Prompter:
    timestamp_types = ['string', 'datetime', 'unix', 'unix_ms']

    def __init__(self, pipeline_: Pipeline, default_config: dict, advanced=False):
        self.advanced = advanced
        self.default_config = default_config
        self.config = {'override_source': pipeline_.override_source}
        self.pipeline = pipeline_

    def prompt(self) -> Pipeline:
        self.prompt_config()
        self.pipeline.set_config(self.config)
        return self.pipeline

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
        if self.config['timestamp']['type'] in ['string', 'datetime']:
            self.set_timezone()

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
    def set_timezone(self):
        if not self.advanced:
            return
        timezone = click.prompt('Timezone (e.g. Europe/London)', type=click.STRING,
                                default=self.default_config.get('timezone', 'UTC'))
        if timezone not in pytz.all_timezones:
            raise click.UsageError('Wrong timezone provided')
        self.config['timezone'] = timezone

    def get_default_object_value(self, property_name: str) -> str:
        default = ''
        if property_name in self.default_config and self.default_config[property_name]:
            default = ' '.join([key + ':' + val for key, val in self.default_config[property_name].items()])
        return default

    def set_static_dimensions(self):
        self.config['properties'] = self.default_config.get('properties', {})
        if self.advanced:
            self.config['properties'] = {}
            properties = self.prompt_object('Static dimensions', self.get_default_object_value('properties'))
            for k, v in properties.items():
                self.config['properties'][k.replace(' ', '_').replace('.', '_')] = v.replace(' ', '_').replace('.', '_')

    def set_tags(self):
        self.config['tags'] = self.default_config.get('tags', {})
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
            test_pipeline = pipeline.manager.build_test_pipeline(self.pipeline.source)
            test_pipeline.config = self.config
            preview.print_sample_data(test_pipeline)

    @staticmethod
    @infinite_retry
    def prompt_object(prompt_text, default='') -> dict:
        properties_str = click.prompt(prompt_text, type=click.STRING, default=default)
        result = {}
        for i in properties_str.split():
            pair = i.split(':')
            if len(pair) != 2:
                raise click.UsageError(f'`{properties_str}` wrong format, correct example - key:val key2:val2')
            result[pair[0]] = pair[1]
        return result

    def prompt_days_to_backfill(self):
        self.config['days_to_backfill'] = \
            click.prompt('Collect since (days ago)', type=click.INT,
                         default=self.default_config.get('days_to_backfill', 0))

    def prompt_interval(self, message='Query interval (in seconds)'):
        self.config['interval'] = click.prompt(message, type=click.INT,
                                               default=self.default_config.get('interval'))

    def prompt_delay(self):
        self.config['delay'] = click.prompt('Delay (in minutes)', type=click.INT,
                                            default=self.default_config.get('delay', 0))

    def set_uses_schema(self):
        static_what = self.config.get('static_what', True)
        if (self.advanced or self.default_config.get('uses_schema') is not None) and static_what:
            self.config['uses_schema'] = click.confirm('Use schema?',
                                                       default=self.default_config.get('uses_schema', True))
            return

        self.config['uses_schema'] = pipeline.manager.supports_schema(self.pipeline) and static_what
