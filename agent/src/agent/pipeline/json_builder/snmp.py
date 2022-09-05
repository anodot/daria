from agent.pipeline.json_builder import Builder


class SNMPBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'snmp'

    def _load_config(self):
        super()._load_config()
        self.config['timestamp'] = {'type': 'unix'}
        self.config['uses_schema'] = True
        self._add_default_dimensions()
        self._add_default_oids()
        self._add_table_oids()
        return self.config

    def _add_default_dimensions(self):
        dimensions = set(self.config.get('dimensions', []))
        dimensions = dimensions.union(self.config.get('dimension_value_paths', {}))
        self.config['dimensions'] = list(dimensions)

    def _add_default_oids(self):
        self.config['dimension_oids'] = list(self.config.get('dimension_value_paths', {}).values())
        self.config['values_oids'] = list(self.config.get('values', {}).keys())

    def _add_table_oids(self):
        if 'oid_table' not in self.config:
            return
        self.config['table_oids'] = []
        if 'dimensions' not in self.config:
            self.config['dimensions'] = []
        if 'values' not in self.config:
            self.config['values'] = {}

        for k, v in self.config['oid_table'].items():
            oid_names = set()
            oid_names = oid_names.union(v['values'].keys())
            oid_names = oid_names.union(v['dimensions'])
            use_indexes = v.get('use_indexes', [])
            self.config['table_oids'].append((k, v['mib'], list(oid_names), use_indexes))
            self.config['dimensions'].extend(v['dimensions'])
            self.config['values'].update(v['values'])


class SNMPRawBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'snmp'
    VALIDATION_SCHEMA_DIR_NAME = 'json_schema_definitions/raw'

    def _load_config(self):
        super()._load_config()
        self.config['timestamp'] = {'type': 'unix'}
        return self.config
