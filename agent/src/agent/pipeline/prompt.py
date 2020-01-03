import click

from agent.pipeline.config_handlers import expression_parser
from agent.tools import infinite_retry, if_validation_enabled, dict_get_nested
from agent.pipeline.pipeline import Pipeline
from urllib.parse import urljoin


class PromptConfig:
    def __init__(self, pipeline: Pipeline):
        self.advanced = False
        self.default_config = {}
        self.config = {}
        self.pipeline = pipeline

    def prompt(self, default_config, advanced=False):
        self.advanced = advanced
        self.default_config = default_config
        self.config = dict()

        self.set_config()
        return self.config

    def set_config(self):
        pass

    def set_timestamp(self):
        self.config['timestamp'] = self.default_config.get('timestamp', {})
        self.config['timestamp']['name'] = self.prompt_property('Timestamp property name',
                                                                self.config['timestamp'].get('name'))
        self.config['timestamp']['type'] = click.prompt('Timestamp property type',
                                                        type=click.Choice(
                                                            ['string', 'datetime', 'unix', 'unix_ms']),
                                                        default=self.config['timestamp'].get('type', 'unix'))

        if self.config['timestamp']['type'] == 'string':
            self.config['timestamp']['format'] = click.prompt('Timestamp format string', type=click.STRING,
                                                              default=self.config['timestamp'].get('format'))

    @infinite_retry
    def prompt_property(self, text: str, default_value) -> str:
        value = click.prompt(text, type=click.STRING, default=default_value)
        self.validate_properties_names([value])
        return value

    @infinite_retry
    def prompt_dimensions(self, text: str, default_value: list) -> list:
        dimensions = click.prompt(text, type=click.STRING, value_proc=lambda x: x.split(), default=default_value)
        self.validate_properties_names(dimensions)
        return dimensions

    def set_dimensions(self):
        self.config['dimensions'] = self.default_config.get('dimensions', {})
        self.config['dimensions']['required'] = self.prompt_dimensions('Required dimensions',
                                                                       self.config['dimensions'].get('required', []))
        self.config['dimensions']['optional'] = click.prompt('Optional dimensions', type=click.STRING,
                                                             value_proc=lambda x: x.split(),
                                                             default=self.config['dimensions'].get('optional', []))

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
            self.prompt_object('tags', 'Tags')

    def set_measurement_name(self):
        self.config['measurement_name'] = click.prompt('Measurement name', type=click.STRING,
                                                       default=self.default_config.get('measurement_name'))

    def set_target_type(self):
        self.config['target_type'] = click.prompt('Target type', type=click.Choice(['counter', 'gauge']),
                                                  default=self.default_config.get('target_type', 'gauge'))

    @if_validation_enabled
    def validate_properties_names(self, names):
        if not self.pipeline.source.sample_data:
            return
        errors = []
        for value in names:
            for record in self.pipeline.source.sample_data:
                if not dict_get_nested(record, value.split('/')):
                    print(f'Property {value} is not present in a sample record')
                    errors.append(value)
                    break
        if errors and not click.confirm('Continue?'):
            raise click.UsageError('Try again')

    @if_validation_enabled
    def data_preview(self):
        if click.confirm('Would you like to see the data preview?', default=True):
            self.pipeline.source.print_sample_data()


class PromptConfigMongo(PromptConfig):
    def set_config(self):
        self.data_preview()
        self.set_measurement_name()
        self.set_value()
        self.set_target_type()
        self.set_timestamp()
        self.set_dimensions()
        self.set_static_properties()
        self.set_tags()

    @infinite_retry
    def prompt_value(self):
        self.config['value']['value'] = click.prompt('Value property name', type=click.STRING,
                                                     default=self.config['value'].get('value'))
        self.validate_properties_names([self.config['value']['value']])

    def set_value(self):
        self.config['value'] = self.default_config.get('value', {})
        if self.advanced or self.config['value'].get('type') == 'constant':
            self.config['value']['value'] = click.prompt('Value (property name or constant value)', type=click.STRING,
                                                         default=self.config['value'].get('value'))
            self.config['value']['type'] = click.prompt('Value type', type=click.Choice(['property', 'constant']),
                                                        default=self.config['value'].get('type'))
        else:
            self.config['value']['type'] = 'property'
            self.prompt_value()


class PromptConfigKafka(PromptConfig):
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

    @infinite_retry
    def prompt_values(self):
        self.prompt_object('values', 'Value properties with target types. Example - property:counter property2:gauge')

        if not set(self.config['values'].values()).issubset(('counter', 'gauge')) and self.static_what():
            raise click.UsageError('Target type should be counter or gauge')
        self.validate_properties_names(self.config['values'].keys())
        if not self.static_what():
            self.validate_properties_names(self.config['values'].values())

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
            self.validate_properties_names(self.config['measurement_names'].values())

    def set_timestamp(self):
        self.config['timestamp'] = self.default_config.get('timestamp', {})
        self.config['timestamp']['name'] = self.prompt_property('Timestamp property name',
                                                                self.config['timestamp'].get('name'))
        self.config['timestamp']['type'] = click.prompt('Timestamp property type',
                                                        type=click.Choice(['string', 'unix', 'unix_ms']),
                                                        default=self.config['timestamp'].get('type', 'unix'))

        if self.config['timestamp']['type'] == 'string':
            self.config['timestamp']['format'] = click.prompt('Timestamp format string', type=click.STRING,
                                                              default=self.config['timestamp'].get('format'))

    @infinite_retry
    def prompt_files(self):
        file = click.prompt('Transformations files paths', type=click.Path(),
                            default=self.config['transform'].get('file', '')).strip()
        if not file:
            return

        expression_parser.transformation.validate_file(file)

        self.config['transform']['file'] = file

    @infinite_retry
    def prompt_condition(self):
        condition = click.prompt('Filter condition', type=click.STRING,
                                 default=self.config['filter'].get('condition', '')).strip()
        if not condition:
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


class PromptConfigInflux(PromptConfig):
    def set_config(self):
        self.set_measurement_name()
        self.pipeline.source.config['conf.resourceUrl'] = self.get_test_url()
        self.data_preview()
        self.set_value()
        self.set_target_type()
        self.set_timestamp()
        self.set_dimensions()
        self.set_static_properties()
        self.set_tags()
        self.set_delay()
        self.set_filtering()

    def get_test_url(self):
        source_config = self.pipeline.source.config
        query = f"select+%2A+from+{self.config['measurement_name']}+limit+{self.pipeline.source.MAX_SAMPLE_RECORDS}"
        return urljoin(source_config['host'], f"/query?db={source_config['db']}&epoch=ns&q={query}")

    def set_delay(self):
        self.config['delay'] = click.prompt('Delay', type=click.STRING, default=self.default_config.get('delay', '0s'))
        self.config['interval'] = click.prompt('Interval, seconds', type=click.INT,
                                               default=self.default_config.get('interval', 60))

    def set_timestamp(self):
        pass

    @infinite_retry
    def set_value(self):
        self.config['value'] = self.default_config.get('value', {'constant': 1, 'values': []})

        self.config['value']['type'] = 'column'
        default_names = self.config['value'].get('values')
        default_names = ' '.join(default_names) if len(default_names) > 0 else None
        self.config['value']['values'] = click.prompt('Value columns names', type=click.STRING,
                                                      default=default_names).split()
        self.validate_properties_names(self.config['value']['values'])
        self.config['value']['constant'] = '1'

    def set_dimensions(self):
        self.config['dimensions'] = self.default_config.get('dimensions', {})
        required = self.config['dimensions'].get('required', [])
        if self.advanced or len(required) > 0:
            self.config['dimensions']['required'] = self.prompt_dimensions('Required dimensions', required)
            self.config['dimensions']['optional'] = click.prompt('Optional dimensions', type=click.STRING,
                                                                 value_proc=lambda x: x.split(),
                                                                 default=self.config['dimensions'].get('optional', []))
        else:
            self.config['dimensions']['required'] = []
            self.config['dimensions']['optional'] = self.prompt_dimensions('Dimensions',
                                                                           self.config['dimensions'].get('optional',
                                                                                                         []))

    def set_filtering(self):
        if self.advanced or self.config.get('filtering', ''):
            self.config['filtering'] = click.prompt('Filtering condition', type=click.STRING,
                                                    default=self.default_config.get('filtering')).strip()


class PromptConfigJDBC(PromptConfig):
    def set_config(self):
        self.set_table()
        self.set_pagination()
        query = f'SELECT * FROM {self.config["table"]}  WHERE {self.config["offset_column"]} > ${{OFFSET}} ORDER BY {self.config["offset_column"]} LIMIT {self.pipeline.source.MAX_SAMPLE_RECORDS}'
        self.pipeline.source.config['query'] = query
        self.pipeline.source.config['offsetColumn'] = self.config['offset_column']
        self.data_preview()
        self.set_values()
        self.set_timestamp()
        self.set_dimensions()
        self.set_static_properties()
        self.set_tags()
        self.set_condition()

    @infinite_retry
    def prompt_values(self):
        self.prompt_object('values', 'Value columns with target types. Example - column:counter column2:gauge')
        if not set(self.config['values'].values()).issubset(('counter', 'gauge')):
            raise click.UsageError('Target type should be counter or gauge')
        self.validate_properties_names(self.config['values'].keys())

    def set_table(self):
        self.config['table'] = click.prompt('Table name', type=click.STRING, default=self.default_config.get('table'))

    def set_values(self):
        self.config['count_records'] = int(click.confirm('Count records?',
                                                         default=self.default_config.get('count_records', False)))
        self.prompt_values()

        if not self.config['count_records'] and not self.config['values']:
            raise click.UsageError('Set value columns or count records flag')

    def set_timestamp(self):
        self.config['timestamp'] = self.default_config.get('timestamp', {})
        self.config['timestamp']['name'] = self.prompt_property('Timestamp column name',
                                                                self.config['timestamp'].get('name'))
        self.config['timestamp']['type'] = click.prompt('Timestamp column type',
                                                        type=click.Choice(['datetime', 'unix', 'unix_ms']),
                                                        default=self.config['timestamp'].get('type', 'unix'))

    def set_dimensions(self):
        self.config['dimensions'] = self.prompt_dimensions('Dimensions', self.default_config.get('dimensions', []))

    def set_pagination(self):
        self.config['limit'] = click.prompt('Limit', type=click.INT,
                                            default=self.default_config.get('limit', 1000))
        self.config['offset_column'] = self.prompt_property('Unique ID column (must be auto-incremented)',
                                                            self.default_config.get('offset_column', 'id'))
        self.config['initial_offset'] = click.prompt('Collect since (days ago)', type=click.STRING,
                                                     default=self.default_config.get('initial_offset', '3'))

    def set_condition(self):
        if self.advanced:
            self.config['condition'] = click.prompt('Condition', type=click.STRING,
                                                    default=self.default_config.get('condition'))
