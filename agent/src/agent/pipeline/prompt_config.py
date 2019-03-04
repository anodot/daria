import click


class PromptConfig:
    def __init__(self, default_config, advanced=False):
        self.advanced = advanced
        self.default_config = default_config
        self.config = dict()

        self.set_measurement_name()
        self.set_value()
        self.set_target_type()
        self.set_timestamp()
        self.set_dimensions()

    def set_measurement_name(self):
        self.config['measurement_name'] = click.prompt('Measurement name', type=click.STRING,
                                                       default=self.default_config.get('measurement_name'))

    def set_value(self):
        self.config['value'] = self.default_config.get('value', {})
        if self.advanced or self.config['value'].get('type') == 'constant':
            self.config['value']['value'] = click.prompt('Value (column name or constant value)', type=click.STRING,
                                                         default=self.config['value'].get('value'))
            self.config['value']['type'] = click.prompt('Value type', type=click.Choice(['column', 'constant']),
                                                        default=self.config['value'].get('type'))
        else:
            self.config['value']['type'] = 'column'
            self.config['value']['value'] = click.prompt('Value column name', type=click.STRING,
                                                         default=self.config['value'].get('value'))

    def set_target_type(self):
        self.config['target_type'] = click.prompt('Target type', type=click.Choice(['counter', 'gauge']),
                                                  default=self.default_config.get('target_type', 'gauge'))

    def set_timestamp(self):
        self.config['timestamp'] = self.default_config.get('timestamp', {})
        self.config['timestamp']['name'] = click.prompt('Timestamp column name', type=click.STRING,
                                                        default=self.config['timestamp'].get('name'))
        self.config['timestamp']['type'] = click.prompt('Timestamp column type',
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


class PromptConfigMongo(PromptConfig):
    pass


class PromptConfigKafka(PromptConfig):
    def set_timestamp(self):
        previous_val = self.default_config.get('timestamp', {}).get('name') == 'kafka_timestamp'
        if click.confirm('Use kafka timestamp?', default=previous_val):
            self.config['timestamp'] = {'name': 'kafka_timestamp', 'type': 'unix_ms'}
        else:
            super().set_timestamp()


pipeline_configs = {
    'mongo': PromptConfigMongo,
    'kafka': PromptConfigKafka
}
