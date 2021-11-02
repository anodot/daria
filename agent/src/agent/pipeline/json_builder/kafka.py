from agent import source
from agent.pipeline.json_builder import Builder


class KafkaBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'kafka'

    def _load_config(self):
        super()._load_config()
        self._load_dimensions()
        if 'timestamp' not in self.config and not self.edit:
            self.config['timestamp'] = {'name': 'kafka_timestamp', 'type': 'unix_ms'}
        if source.KafkaSource.CONFIG_CONSUMER_GROUP not in self.config['override_source']:
            self.config['override_source'][source.KafkaSource.CONFIG_CONSUMER_GROUP] = \
                "agent_" + self.config['pipeline_id']
        return self.config
