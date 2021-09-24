from agent import pipeline
from agent.pipeline.config.stages.base import Stage


class JDBCOffsetScript(Stage):
    JYTHON_SCRIPT = 'jdbc.py'

    def get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            return {
                'scriptConf.params': [
                    {'key': 'INITIAL_OFFSET', 'value': self.get_initial_timestamp().strftime('%d/%m/%Y %H:%M')},
                    {'key': 'INTERVAL_IN_SECONDS', 'value': str(self.pipeline.interval)},
                    {'key': 'DELAY_IN_SECONDS', 'value': str(self.pipeline.delay)},
                ],
                'script': f.read(),
            }


class JDBCRawTransformScript(Stage):
    def get_config(self) -> dict:
        return {
            'userParams': [
                {'key': 'QUERY', 'value': pipeline.jdbc.query.TemplateBuilder(self.pipeline).build()},
                {'key': 'LAST_TIMESTAMP_TEMPLATE', 'value': pipeline.jdbc.query.LAST_TIMESTAMP_TEMPLATE},
                {
                    'key': 'LOGGING_OF_QUERIES_ENABLED',
                    'value': 'true' if bool(self.pipeline.config.get('logging_of_queries_enabled', True)) else ''
                },
            ],
        }
# todo я еще не сделал max_number_of_metrics
