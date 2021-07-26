from agent import source
from agent.pipeline.config.stages.base import Stage


class PromQLScript(Stage):
    JYTHON_SCRIPT = 'promql.py'

    def _get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            return {
                'scriptConf.params': [
                    {'key': 'URL', 'value': self.pipeline.source.config[source.PromQLSource.URL]},
                    {'key': 'USERNAME',
                     'value': self.pipeline.source.config.get(source.PromQLSource.USERNAME, '')},
                    {'key': 'PASSWORD',
                     'value': self.pipeline.source.config.get(source.PromQLSource.PASSWORD, '')},
                    {'key': 'QUERY', 'value': self.pipeline.config['query']},
                    {'key': 'INITIAL_TIMESTAMP', 'value': str(int(self.get_initial_timestamp().timestamp()))},
                    {'key': 'INTERVAL', 'value': str(self.pipeline.interval)},
                    {'key': 'DELAY_IN_MINUTES', 'value': str(self.pipeline.delay)},
                    {
                        'key': 'VERIFY_SSL',
                        'value': '1' if self.pipeline.source.config.get(source.APISource.VERIFY_SSL, True) else ''
                    },
                    {'key': 'QUERY_TIMEOUT', 'value': str(self.pipeline.source.query_timeout)},
                    {'key': 'AGGREGATED_METRIC_NAME', 'value': str(self.pipeline.config.get('aggregated_metric_name'))},
                ],
                'script': f.read(),
            }
