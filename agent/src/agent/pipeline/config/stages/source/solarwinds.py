import urllib.parse

from agent import source, pipeline, monitoring
from agent.pipeline.config.stages.base import JythonSource


class SolarWindsScript(JythonSource):
    JYTHON_SCRIPT = 'solarwinds.py'
    SOLARWINDS_API_ADDRESS = '/SolarWinds/InformationService/v3/Json/Query'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'PIPELINE_NAME',
                'value': self.pipeline.name
            },
            {
                'key': 'QUERY',
                'value': pipeline.jdbc.query.SolarWindsBuilder(self.pipeline).build()
            },
            {
                'key': 'SOLARWINDS_API_URL',
                'value': urllib.parse.urljoin(
                    self.pipeline.source.config[source.SolarWindsSource.URL], self.SOLARWINDS_API_ADDRESS
                )
            },
            {
                'key': 'API_USER',
                'value': self.pipeline.source.config[source.SolarWindsSource.USERNAME]
            },
            {
                'key': 'API_PASSWORD',
                'value': self.pipeline.source.config[source.SolarWindsSource.PASSWORD]
            },
            {
                'key': 'INTERVAL_IN_SECONDS',
                'value': str(self.pipeline.interval)
            },
            {
                'key': 'DELAY_IN_SECONDS',
                'value': str(self.pipeline.delay)
            },
            {
                'key': 'DAYS_TO_BACKFILL',
                'value': self.pipeline.days_to_backfill
            },
            {
                'key': 'QUERY_TIMEOUT',
                'value': str(self.pipeline.source.query_timeout)
            },
            {
                'key': 'MONITORING_URL',
                'value': monitoring.get_monitoring_source_error_url(self.pipeline)
            },
            {
                'key': 'VERIFY_SSL',
                'value': '1' if self.pipeline.source.config.get('verify_ssl', True) else ''
            },
        ]
