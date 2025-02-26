from urllib.parse import urljoin
from agent import pipeline
from agent.pipeline.config.stages.base import JythonSource, JythonProcessor


class JDBCOffsetScript(JythonSource):
    JYTHON_SCRIPT = 'jdbc.py'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'INITIAL_OFFSET',
                'value': str(self.get_initial_timestamp().timestamp()),
            },
            {
                'key': 'INTERVAL_IN_SECONDS',
                'value': str(self.pipeline.interval),
            },
            {
                'key': 'DELAY_IN_SECONDS',
                'value': str(self.pipeline.delay),
            },
            {
                'key': 'WATERMARK_IN_LOCAL_TIMEZONE',
                'value': str(self.pipeline.watermark_in_local_timezone),
            },
            {
                'key': 'TIMEZONE',
                'value': str(self.pipeline.timezone),
            },
            {
                'key': 'QUERY_MISSING_DATA_INTERVAL',
                'value': str(self.pipeline.config.get('query_missing_data_interval', ''))
            },
            {
                'key': 'PIPELINE_OFFSET_ENDPOINT',
                'value': urljoin(self.pipeline.streamsets.agent_external_url, f'/pipeline-offset/{self.pipeline.name}')
            },
            {
                'key': 'DISABLE_BACKFILL',
                'value': str(int(self.pipeline.disable_backfill))
            }
        ]


class JDBCRawTransformScript(JythonProcessor):
    JYTHON_SCRIPT = 'raw_jdbc_transform.py'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'QUERY',
                'value': pipeline.jdbc.query.TemplateBuilder(self.pipeline).build(),
            },
            {
                'key': 'LAST_TIMESTAMP_TEMPLATE',
                'value': pipeline.jdbc.query.LAST_TIMESTAMP_TEMPLATE,
            },
            {
                'key': 'LOGGING_OF_QUERIES_ENABLED',
                'value': 'true' if bool(self.pipeline.config.get('logging_of_queries_enabled', True)) else '',
            },
        ]
