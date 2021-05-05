from agent import source
from agent.pipeline.config.stages.source.jdbc import JDBCSource


class SolarWindsScript(JDBCSource):
    JYTHON_SCRIPT = 'solarwinds.py'
    LAST_TIMESTAMP = '%last_timestamp%'

    def _get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            return {
                'scriptConf.params': [
                    {'key': 'PIPELINE_NAME', 'value': self.pipeline.name},
                    {'key': 'QUERY', 'value': self.get_query()},
                    {'key': 'SOLARWINDS_API_URL', 'value': self.pipeline.source.config[source.SolarWindsSource.URL]},
                    {'key': 'API_USER', 'value': self.pipeline.source.config[source.SolarWindsSource.USERNAME]},
                    {'key': 'API_PASSWORD', 'value': self.pipeline.source.config[source.SolarWindsSource.PASSWORD]},
                    {'key': 'INTERVAL_IN_SECONDS', 'value': str(self.pipeline.interval)},
                    {'key': 'DELAY_IN_SECONDS', 'value': str(self.pipeline.delay)},
                    {'key': 'DAYS_TO_BACKFILL', 'value': self.pipeline.days_to_backfill},
                    {'key': 'DATEFORMAT', 'value': self.pipeline.days_to_backfill},
                ],
                'script': f.read()
            }

    def _get_timestamp_condition(self) -> str:
        date_time = f"DateTime('{self.LAST_TIMESTAMP}')"
        return f'{self._timestamp_to_unix} > {date_time}' \
               f' AND {self._timestamp_to_unix} <= AddSecond({self.pipeline.interval}, {date_time})'
