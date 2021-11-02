from agent.pipeline.json_builder import Builder


class InfluxBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'influx'

    def _load_config(self):
        super()._load_config()
        self._load_dimensions()
        self._set_timestamp()
        return self.config

    def _set_timestamp(self):
        self.config['timestamp'] = {
            'type': 'unix_ms',
            'name': 'time',
        }


class Influx2Builder(InfluxBuilder):
    VALIDATION_SCHEMA_FILE_NAME = 'influx2'

    def _load_config(self):
        super()._load_config()
        self.config['uses_schema'] = True
        return self.config

    def _set_timestamp(self):
        self.config['timestamp'] = {
            'type': 'unix',
            'name': '_time',
        }
