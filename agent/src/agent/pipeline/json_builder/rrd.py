from agent.pipeline.json_builder import Builder


class RRDBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'rrd'

    def _load_config(self):
        super()._load_config()
        if 'convert_bytes_into_bits' not in self.config and not self.edit:
            self.config['convert_bytes_into_bits'] = False
        if 'timestamp' not in self.config:
            self.config['timestamp'] = {'type': 'unix'}
        return self.config
