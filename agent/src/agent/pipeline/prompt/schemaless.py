import click

from agent.pipeline.config import expression_parser
from agent.tools import infinite_retry, dict_get_nested
from .base import PromptConfig


class PromptConfigSchemaless(PromptConfig):
    timestamp_types = ['string', 'unix', 'unix_ms']
    target_types = ['counter', 'gauge']

    def set_config(self):
        self.data_preview()
        self.set_values()
        self.set_measurement_names()
        self.set_timestamp()
        self.set_dimensions()
        self.set_static_properties()
        self.set_tags()
        self.filter()
        self.transform()

    def static_what(self):
        return self.config.get('static_what', True)

    def __get_values_array(self, records) -> list:
        if self.config.get('values_array_path') and len(records) > 0:
            return dict_get_nested(records[0], self.config['values_array_path'].split('/'))
        return records

    @infinite_retry
    def prompt_values(self):
        self.prompt_object('values', 'Value properties with target types. Example - property:counter property2:gauge')

        if not set(self.config['values'].values()).issubset(self.target_types) and self.static_what():
            raise click.UsageError(f'Target type should be on of: {", ".join(self.target_types)}')

        values_array = self.__get_values_array(self.pipeline.source.sample_data)
        self.validate_properties_names(self.config['values'].keys(), values_array)
        if not self.static_what():
            t_types_paths = [t_type for t_type in self.config['values'].values() if t_type not in self.target_types]
            self.validate_properties_names(t_types_paths, values_array)

    @infinite_retry
    def set_values(self):
        self.config['count_records'] = int(click.confirm('Count records?',
                                                         default=self.default_config.get('count_records', False)))
        if self.config['count_records']:
            self.config['count_records_measurement_name'] = click.prompt('Measurement name', type=click.STRING,
                                                                         default=self.default_config.get(
                                                                             'count_records_measurement_name'))

        static_what_default = self.default_config.get('static_what', True)
        if self.advanced or not static_what_default:
            self.config['static_what'] = click.confirm('Is `what` property static?',
                                                       default=self.default_config.get('static_what', True))
            self.config['values_array_path'] = click.prompt('Values array path', type=click.STRING,
                                                            default=self.default_config.get('values_array_path', ''))

        self.prompt_values()
        if not self.config['count_records'] and not self.config['values']:
            raise click.UsageError('Set value properties or count records flag')

    @infinite_retry
    def set_measurement_names(self):
        prompt_text = 'Measurement names' if self.config.get('static_what', True) else 'Measurement properties names'
        self.prompt_object('measurement_names', prompt_text + '. Example -  property:measure property2:measure2')
        if not set(self.config['measurement_names'].keys()).issubset(set(self.config['values'].keys())):
            raise click.UsageError('Wrong property name')
        if not self.static_what():
            values_array = self.__get_values_array(self.pipeline.source.sample_data)
            self.validate_properties_names(self.config['measurement_names'].values(), values_array)

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
    def prompt_files(self):
        file = click.prompt('Transformations files paths', type=click.Path(),
                            default=self.config['transform'].get('file', '')).strip()
        if not file:
            del self.config['transform']
            return

        expression_parser.transformation.validate_file(file)

        self.config['transform']['file'] = file

    @infinite_retry
    def prompt_condition(self):
        condition = click.prompt('Filter condition', type=click.STRING,
                                 default=self.config['filter'].get('condition', '')).strip()
        if not condition:
            del self.config['filter']
            return
        expression_parser.condition.validate(condition)
        self.config['filter']['condition'] = condition

    def filter(self):
        if not self.advanced and not self.default_config.get('filter'):
            return
        self.config['filter'] = self.default_config.get('filter', {})
        self.prompt_condition()

    def transform(self):
        if not self.advanced and not self.default_config.get('transform'):
            return
        self.config['transform'] = self.default_config.get('transform', {})
        self.prompt_files()
