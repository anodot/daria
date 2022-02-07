from agent import pipeline
from agent.pipeline.json_builder import Builder


class PromQLBuilder(Builder):
    VALUE = '__value'
    VALIDATION_SCHEMA_FILE_NAME = 'promql'

    def _load_config(self):
        super()._load_config()
        self.config['timestamp'] = {'name': 'timestamp', 'type': pipeline.TimestampType.UNIX.value}
        # this is needed due to the specific way promql source and transformations work
        if self.config.get('values'):
            self.config['measurement_names'] = self._get_measurement_names()
            self.config['values'] = self._change_values()
        return self.config

    def _get_measurement_names(self):
        if len(self.config['values']) > 1:
            raise Exception('Only one value is supported')
        return {self.VALUE: v for v in self.config['values']}

    def _change_values(self):
        if len(self.config['values']) > 1:
            raise Exception('Only one value is supported')
        return {self.VALUE: 'gauge' for _ in self.config['values']}
