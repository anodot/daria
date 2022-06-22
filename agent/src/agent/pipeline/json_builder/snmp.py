from agent.pipeline.json_builder import Builder


class SNMPBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'snmp'

    def _load_config(self):
        super()._load_config()
        self.config['timestamp'] = {'type': 'unix'}
        self.config['uses_schema'] = True
        self._add_default_dimensions()
        self._add_default_oids()
        return self.config

    def _add_default_dimensions(self):
        dimensions = set(self.config.get('dimensions', []))
        dimensions = dimensions.union(self.config['dimension_value_paths'])
        self.config['dimensions'] = list(dimensions)

    def _add_default_oids(self):
        oids = set(self.config.get('oids', []))
        oids = oids.union(self.config['dimension_value_paths'].values())
        oids = oids.union(self.config['values'].keys())
        self.config['oids'] = list(oids)


class SNMPRawBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'snmp'
    VALIDATION_SCHEMA_DIR_NAME = 'json_schema_definitions/raw'

    def _load_config(self):
        super()._load_config()
        self.config['timestamp'] = {'type': 'unix'}
        return self.config
