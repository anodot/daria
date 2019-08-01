import click


class PromptConfig:
    def __init__(self, default_config, advanced=False):
        self.advanced = advanced
        self.default_config = default_config
        self.config = dict()

        self.set_config()

    def set_config(self):
        self.set_measurement_name()
        self.set_value()
        self.set_target_type()
        self.set_timestamp()
        self.set_dimensions()
        self.set_static_properties()

    def set_measurement_name(self):
        self.config['measurement_name'] = click.prompt('Measurement name', type=click.STRING,
                                                       default=self.default_config.get('measurement_name'))

    def set_value(self):
        self.config['value'] = self.default_config.get('value', {})
        if self.advanced or self.config['value'].get('type') == 'constant':
            self.config['value']['value'] = click.prompt('Value (property name or constant value)', type=click.STRING,
                                                         default=self.config['value'].get('value'))
            self.config['value']['type'] = click.prompt('Value type', type=click.Choice(['property', 'constant']),
                                                        default=self.config['value'].get('type'))
        else:
            self.config['value']['type'] = 'property'
            self.config['value']['value'] = click.prompt('Value property name', type=click.STRING,
                                                         default=self.config['value'].get('value'))

    def set_target_type(self):
        self.config['target_type'] = click.prompt('Target type', type=click.Choice(['counter', 'gauge']),
                                                  default=self.default_config.get('target_type', 'gauge'))

    def set_timestamp(self):
        self.config['timestamp'] = self.default_config.get('timestamp', {})
        self.config['timestamp']['name'] = click.prompt('Timestamp property name', type=click.STRING,
                                                        default=self.config['timestamp'].get('name'))
        self.config['timestamp']['type'] = click.prompt('Timestamp property type',
                                                        type=click.Choice(
                                                            ['string', 'datetime', 'unix', 'unix_ms']),
                                                        default=self.config['timestamp'].get('type', 'unix'))

        if self.config['timestamp']['type'] == 'string':
            self.config['timestamp']['format'] = click.prompt('Timestamp format string', type=click.STRING,
                                                              default=self.config['timestamp'].get('format'))

    def set_dimensions(self):
        self.config['dimensions'] = self.default_config.get('dimensions', {})
        self.config['dimensions']['required'] = click.prompt('Required dimensions',
                                                             type=click.STRING,
                                                             value_proc=lambda x: x.split(),
                                                             default=self.config['dimensions'].get('required',
                                                                                                   []))
        self.config['dimensions']['optional'] = click.prompt('Optional dimensions',
                                                             type=click.STRING,
                                                             value_proc=lambda x: x.split(),
                                                             default=self.config['dimensions'].get('optional',
                                                                                                   []))

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


class PromptConfigMongo(PromptConfig):
    pass


class PromptConfigKafka(PromptConfig):

    def set_measurement_name(self):
        static_what_default = self.default_config.get('static_what', True)
        if self.advanced or not static_what_default:
            self.config['static_what'] = click.confirm('Is `what` property static?',
                                                       default=self.default_config.get('static_what', True))

        prompt_text = 'Measurement name' if self.config.get('static_what', True) else 'Measurement property name'
        self.config['measurement_name'] = click.prompt(prompt_text, type=click.STRING,
                                                       default=self.default_config.get('measurement_name'))

    def set_target_type(self):
        if self.config.get('static_what', True):
            self.config['target_type'] = click.prompt('Target type', type=click.Choice(['counter', 'gauge']),
                                                      default=self.default_config.get('target_type', 'gauge'))
        else:
            self.config['target_type'] = click.prompt('Target type property name', type=click.STRING,
                                                      default=self.default_config.get('target_type'))

    def set_timestamp(self):
        previous_val = self.default_config.get('timestamp', {}).get('name') == 'kafka_timestamp'
        if click.confirm('Use kafka timestamp?', default=previous_val):
            self.config['timestamp'] = {'name': 'kafka_timestamp', 'type': 'unix_ms'}
        else:
            self.config['timestamp'] = self.default_config.get('timestamp', {})
            self.config['timestamp']['name'] = click.prompt('Timestamp property name', type=click.STRING,
                                                            default=self.config['timestamp'].get('name'))
            self.config['timestamp']['type'] = click.prompt('Timestamp property type',
                                                            type=click.Choice(['string', 'unix', 'unix_ms']),
                                                            default=self.config['timestamp'].get('type', 'unix'))

            if self.config['timestamp']['type'] == 'string':
                self.config['timestamp']['format'] = click.prompt('Timestamp format string', type=click.STRING,
                                                                  default=self.config['timestamp'].get('format'))


class PromptConfigInflux(PromptConfig):
    def set_timestamp(self):
        pass

    def set_value(self):
        self.config['value'] = self.default_config.get('value', {'constant': 1, 'values': []})
        if self.advanced or self.config['value'].get('type') == 'constant':
            self.config['value']['type'] = click.prompt('Value type', type=click.Choice(['column', 'constant']),
                                                        default=self.config['value'].get('type'))

            value = click.prompt('Value (column name or constant value)', type=click.STRING,
                                 default=self.config['value'].get('constant'))
            if self.config['value']['type'] == 'constant':
                self.config['value']['constant'] = value
                self.config['value']['values'] = []
            else:
                self.config['value']['constant'] = 1
                self.config['value']['values'] = value.split()
        else:
            self.config['value']['type'] = 'column'
            default_names = self.config['value'].get('values')
            default_names = ' '.join(default_names) if len(default_names) > 0 else None
            self.config['value']['values'] = click.prompt('Value columns names', type=click.STRING,
                                                          default=default_names).split()
            self.config['value']['constant'] = '1'

    def set_dimensions(self):
        self.config['dimensions'] = self.default_config.get('dimensions', {})
        required = self.config['dimensions'].get('required', [])
        if self.advanced or len(required) > 0:
            self.config['dimensions']['required'] = click.prompt('Required dimensions',
                                                                 type=click.STRING,
                                                                 value_proc=lambda x: x.split(),
                                                                 default=required)
            self.config['dimensions']['optional'] = click.prompt('Optional dimensions',
                                                                 type=click.STRING,
                                                                 value_proc=lambda x: x.split(),
                                                                 default=self.config['dimensions'].get('optional',
                                                                                                       []))
        else:
            self.config['dimensions']['required'] = []
            self.config['dimensions']['optional'] = click.prompt('Dimensions',
                                                                 type=click.STRING,
                                                                 value_proc=lambda x: x.split(),
                                                                 default=self.config['dimensions'].get('optional',
                                                                                                       []))


class PromptConfigJDBC(PromptConfig):
    def set_config(self):
        self.set_table()
        self.set_values()
        self.set_timestamp()
        self.set_dimensions()
        self.set_static_properties()
        self.set_pagination()
        self.set_condition()

    def set_table(self):
        self.config['table'] = click.prompt('Table name', type=click.STRING, default=self.default_config.get('table'))

    def set_values(self):
        self.config['count_records'] = int(click.confirm('Count records?',
                                                         default=self.default_config.get('count_records', False)))
        self.prompt_object('values', 'Value columns with target types. Example - column:counter column2:gauge')

        if not set(self.config['values'].values()).issubset(('counter', 'gauge')):
            raise click.UsageError('Target type should be counter or gauge')

        if not self.config['count_records'] and not self.config['values']:
            raise click.UsageError('Set value columns or count records flag')

    def set_timestamp(self):
        self.config['timestamp'] = self.default_config.get('timestamp', {})
        self.config['timestamp']['name'] = click.prompt('Timestamp column name', type=click.STRING,
                                                        default=self.config['timestamp'].get('name'))
        self.config['timestamp']['type'] = click.prompt('Timestamp column type',
                                                        type=click.Choice(['datetime', 'unix', 'unix_ms']),
                                                        default=self.config['timestamp'].get('type', 'unix'))

    def set_dimensions(self):
        self.config['dimensions'] = click.prompt('Dimensions', type=click.STRING, value_proc=lambda x: x.split(),
                                                 default=self.default_config.get('dimensions', []))

    def set_pagination(self):
        self.config['limit'] = click.prompt('Limit', type=click.INT,
                                            default=self.default_config.get('limit', 1000))
        self.config['offset_column'] = click.prompt('Unique ID column (must be auto-incremented)', type=click.STRING,
                                                    default=self.default_config.get('offset_column', 'id'))
        self.config['initial_offset'] = click.prompt('Collect since (days ago)', type=click.STRING,
                                                     default=self.default_config.get('initial_offset', '3'))

    def set_condition(self):
        if self.advanced:
            self.config['condition'] = click.prompt('Condition', type=click.STRING,
                                                    default=self.default_config.get('condition'))
