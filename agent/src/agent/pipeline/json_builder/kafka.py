from agent import source
from agent.pipeline.json_builder import Builder
from agent.modules import constants


class KafkaBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'kafka'

    def _load_config(self):
        super()._load_config()
        self._load_dimensions()
        if 'timestamp' not in self.config and not self.edit:
            self.config['timestamp'] = {'name': 'kafka_timestamp', 'type': 'unix_ms'}
        if source.KafkaSource.CONFIG_CONSUMER_GROUP not in self.config['override_source']:
            self.config['override_source'][source.KafkaSource.CONFIG_CONSUMER_GROUP] = \
                constants.KAFKA_CONSUMER_GROUP_PREFIX + self.config['pipeline_id']
        return self.config


class KafkaRawBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'kafka'
    VALIDATION_SCHEMA_DIR_NAME = 'json_schema_definitions/raw'
