from agent.pipeline.json_builder import Builder


class CactiBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'cacti'

    def _load_config(self):
        super()._load_config()
        if 'timestamp' not in self.config:
            self.config['timestamp'] = {'type': 'unix'}
        if 'add_graph_name_dimension' not in self.config and not self.edit:
            self.config['add_graph_name_dimension'] = False
        if 'convert_bytes_into_bits' not in self.config and not self.edit:
            self.config['convert_bytes_into_bits'] = False
        return self.config
