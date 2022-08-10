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
        dimensions = dimensions.union(self.config['dimension_value_paths'])
        self.config['dimensions'] = list(dimensions)

    def _add_default_oids(self):
        self.config['dimension_oids'] = list(self.config['dimension_value_paths'].values())
        self.config['values_oids'] = list(self.config['values'].keys())

    def _add_table_oids(self):
        self.config['table_oids'] = []
        for k, v in self.config['oid_table'].items():
            oid_names = set()
            oid_names = oid_names.union(v['values'].keys())
            oid_names = oid_names.union(v['dimensions'])
            self.config['table_oids'].append((k, v['mib'], list(oid_names)))

            self.config['dimensions'].extend(v['dimensions'])
            self.config['values'].update(v['values'])


class SNMPRawBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'snmp'
    VALIDATION_SCHEMA_DIR_NAME = 'json_schema_definitions/raw'

    def _load_config(self):
        super()._load_config()
        self.config['timestamp'] = {'type': 'unix'}
        return self.config
