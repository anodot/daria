from agent.pipeline.json_builder import Builder
from agent.data_extractor.snmp import snmp


class SNMPBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'snmp'

    def _load_config(self):
        super()._load_config()
        self.config['timestamp'] = {'type': 'unix'}
        self.config['uses_schema'] = True
        self._add_default_dimensions()
        return self.config

    def _add_default_dimensions(self):
        if 'dimensions' not in self.config:
            self.config['dimensions'] = []
        self.config['oids'].append(snmp.HOSTNAME_OID)
        self.config['dimensions'].append(snmp.HOSTNAME_NAME)
        if 'dimension_value_paths' not in self.config:
            self.config['dimension_value_paths'] = {}
        self.config['dimension_value_paths'][snmp.HOSTNAME_NAME] = snmp.HOSTNAME_PATH


class SNMPRawBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'snmp'
    VALIDATION_SCHEMA_DIR_NAME = 'json_schema_definitions/raw'

    def _load_config(self):
        super()._load_config()
        self.config['timestamp'] = {'type': 'unix'}
        return self.config
