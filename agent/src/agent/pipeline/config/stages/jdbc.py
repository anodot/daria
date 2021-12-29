from agent import pipeline
from agent.pipeline.config.stages.base import JythonSource, JythonProcessor


class JDBCOffsetScript(JythonSource):
    JYTHON_SCRIPT = 'jdbc.py'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'INITIAL_OFFSET',
                'value': self.get_initial_timestamp().strftime('%d/%m/%Y %H:%M')
            },
            {
                'key': 'INTERVAL_IN_SECONDS',
                'value': str(self.pipeline.interval)
            },
            {
                'key': 'DELAY_IN_SECONDS',
                'value': str(self.pipeline.delay)
            },
        ]


class JDBCRawTransformScript(JythonProcessor):
    JYTHON_SCRIPT = 'raw_jdbc_transform.py'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'QUERY',
                'value': pipeline.jdbc.query.TemplateBuilder(self.pipeline).build()
            },
            {
                'key': 'LAST_TIMESTAMP_TEMPLATE',
                'value': pipeline.jdbc.query.LAST_TIMESTAMP_TEMPLATE
            },
            {
                'key': 'LOGGING_OF_QUERIES_ENABLED',
                'value': 'true' if bool(self.pipeline.config.get('logging_of_queries_enabled', True)) else ''
            },
        ]
