from agent import monitoring, source, pipeline
from agent.pipeline.config.stages.base import JythonSource
from agent.modules import logger


class ElasticScript(JythonSource):
    JYTHON_SCRIPT = 'elastic_loader.py'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'URLs',
                'value': self.pipeline.source.config[source.ElasticSource.CONFIG_HTTP_URIS]
            },
            {
                'key': 'USERNAME',
                'value': self.pipeline.source.config.get(source.ElasticSource.CONFIG_USERNAME, '')
            },
            {
                'key': 'PASSWORD',
                'value': self.pipeline.source.config.get(source.ElasticSource.CONFIG_PASSWORD, '')
            },
            {
                'key': 'VERIFY_SSL',
                'value': '1' if self.pipeline.source.config.get(source.ElasticSource.VERIFY_SSL, True) else ''
            },
            {
                'key': 'INDEX',
                'value': self.pipeline.source.config[source.ElasticSource.CONFIG_INDEX]
            },
            {
                'key': 'INITIAL_TIMESTAMP',
                'value': str(int(self.get_initial_timestamp().timestamp()))
            },
            {
                'key': 'INTERVAL',
                'value': str(self.pipeline.interval)
            },
            {
                'key': 'DELAY_IN_MINUTES',
                'value': str(self.pipeline.delay)
            },
            {
                'key': 'QUERY_TIMEOUT',
                'value': str(self.pipeline.source.query_timeout) + 's'
            },
            {
                'key': 'SCROLL_TIMEOUT',
                'value': str(self.pipeline.source.config.get('scroll_timeout', '5m'))
            },
            {
                'key': 'MONITORING_URL',
                'value': monitoring.get_monitoring_source_error_url(self.pipeline)
            },
            {
                'key': "QUERY",
                'value': self.pipeline.config['query']
            },
            {
                'key': 'DVP_ENABLED',
                'value': str(bool(self.pipeline.dvp_config))
            },
            {
                'key': 'LOG_EVERYTHING',
                'value': '1' if self.pipeline.log_everything else ''
            },
            {
                'key': 'TIMESTAMP_FORMAT',
                'value': self.pipeline.timestamp_format
            },
        ]