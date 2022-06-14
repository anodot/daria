from agent.pipeline.json_builder import Builder
from agent.data_extractor.snmp import snmp


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
        if 'dimensions' not in self.config:
            self.config['dimensions'] = []
        if snmp.HOSTNAME_NAME not in self.config['dimensions']:
            self.config['dimensions'].append(snmp.HOSTNAME_NAME)
        self.config['dimension_value_paths'][snmp.HOSTNAME_NAME] = snmp.HOSTNAME_OID

    def _add_default_oids(self):
        oids = set(self.config.get('oids', []))
        oids = oids.union(self.config['dimension_value_paths'].values())
        oids = oids.union(self.config['values'].keys())
        oids.add(snmp.HOSTNAME_OID)
        self.config['oids'] = list(oids)


class SNMPRawBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'snmp'
    VALIDATION_SCHEMA_DIR_NAME = 'json_schema_definitions/raw'

    def _load_config(self):
        super()._load_config()
        self.config['timestamp'] = {'type': 'unix'}
        return self.config
