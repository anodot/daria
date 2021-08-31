import urllib.parse

from agent import source
from agent.pipeline.config.stages.source.jdbc import JDBCSource


class ObserviumScript(JDBCSource):
    # todo is it different compared to solarwinds or other api?
    JYTHON_SCRIPT = 'observium.py'

    def get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            return {
                'scriptConf.params': [
                    {
                        'key': 'API_URL',
                        'value': urllib.parse.urljoin(
                            self.pipeline.source.config[source.SolarWindsSource.URL],
                            '/api/v0/'
                        )
                    },
                    {'key': 'API_USER', 'value': self.pipeline.source.config[source.ObserviumSource.USERNAME]},
                    {'key': 'API_PASSWORD', 'value': self.pipeline.source.config[source.ObserviumSource.PASSWORD]},
                    {'key': 'INTERVAL_IN_SECONDS', 'value': str(self.pipeline.interval)},
                    {'key': 'DELAY_IN_SECONDS', 'value': str(self.pipeline.delay)},
                    {'key': 'DAYS_TO_BACKFILL', 'value': self.pipeline.days_to_backfill},
                    {'key': 'QUERY_TIMEOUT', 'value': str(self.pipeline.source.query_timeout)},
                    {
                        'key': 'MONITORING_URL',
                        'value': urllib.parse.urljoin(
                            self.pipeline.streamsets.agent_external_url,
                            f'/monitoring/source_http_error/{self.pipeline.name}/'
                        )
                    },
                    {'key': 'VERIFY_SSL', 'value': '1' if self.pipeline.source.config.get('verify_ssl', True) else ''},
                ],
                'script': f.read()
            }
