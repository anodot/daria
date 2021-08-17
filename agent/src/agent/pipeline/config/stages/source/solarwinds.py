import urllib.parse

from agent import source
from agent.pipeline.config.stages.source.jdbc import JDBCSource


class SolarWindsScript(JDBCSource):
    JYTHON_SCRIPT = 'solarwinds.py'
    LAST_TIMESTAMP = '%last_timestamp%'
    SOLARWINDS_API_ADDRESS = '/SolarWinds/InformationService/v3/Json/Query'

    def get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            return {
                'scriptConf.params': [
                    {'key': 'PIPELINE_NAME', 'value': self.pipeline.name},
                    {'key': 'QUERY', 'value': self.get_query()},
                    {
                        'key': 'SOLARWINDS_API_URL',
                        'value': urllib.parse.urljoin(
                            self.pipeline.source.config[source.SolarWindsSource.URL],
                            self.SOLARWINDS_API_ADDRESS
                        )
                    },
                    {'key': 'API_USER', 'value': self.pipeline.source.config[source.SolarWindsSource.USERNAME]},
                    {'key': 'API_PASSWORD', 'value': self.pipeline.source.config[source.SolarWindsSource.PASSWORD]},
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

    def _get_timestamp_condition(self) -> str:
        date_time = f"DateTime('{self.LAST_TIMESTAMP}')"
        return f'{self.pipeline.timestamp_path} > {date_time}' \
               f' AND {self.pipeline.timestamp_path} <= AddSecond({self.pipeline.interval}, {date_time})'
