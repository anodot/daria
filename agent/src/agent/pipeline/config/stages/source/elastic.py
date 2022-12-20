import os

from agent import source, monitoring
from agent.pipeline.config.stages.base import JythonSource


class ElasticScript(JythonSource):
    JYTHON_SCRIPT = 'elastic_loader.py'

    def _load_query_from_file(self):
        with open(self.pipeline.config['query_file']) as f:
            query = f.read()
            return query.replace('${OFFSET}', '"OFFSET"')

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'URLs',
                'value': self.pipeline.source.config['conf.httpUris']
            },
            {
                'key': 'INDEX',
                'value': self.pipeline.source.config['conf.index']
            },
            {
                'key': 'INITIAL_TIMESTAMP',
                'value': str(int(self.get_initial_timestamp().timestamp()))
            },
            {
                'key': 'INTERVAL',
                'value': str(self.pipeline.source.config.get('query_interval_sec', 1))
            },
            {
                'key': 'DELAY_IN_MINUTES',
                'value': str(self.pipeline.delay)
            },
            {
                'key': 'QUERY_TIMEOUT',
                'value': str(self.pipeline.source.query_timeout)
            },
            {
                # Do we need to customize it?
                'key': 'SCROLL_TIMEOUT',
                'value': '5m'
            },
            {
                'key': 'MONITORING_URL',
                'value': monitoring.get_monitoring_source_error_url(self.pipeline)
            },
            {
                'key': "QUERY",
                'value': self._load_query_from_file()
            }
        ]


# class TestElasticScript(JythonSource):
#     JYTHON_SCRIPT = 'elastic_loader.py'
#     JYTHON_SCRIPTS_DIR = os.path.join(JythonSource.JYTHON_SCRIPTS_DIR, 'test_pipelines')
