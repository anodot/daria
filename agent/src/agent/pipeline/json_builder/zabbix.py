from agent.pipeline.json_builder import Builder


class ZabbixBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'zabbix'

    def _load_config(self):
        super()._load_config()
        self.config['timestamp'] = {'type': 'unix', 'name': 'clock'}
        if 'query' in self.pipeline.config and self.pipeline.config['query'] != self.config['query']:
            self.config['query_changed'] = True
        return self.config
