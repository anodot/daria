import re
import os

from agent.pipeline.config.stages.influx import InfluxScript
from agent.pipeline.config.stages.base import JythonSource
from urllib.parse import urljoin, quote_plus

TIMESTAMP_CONDITION = '{TIMESTAMP_CONDITION}'
LAST_TIMESTAMP = '${record:value("/last_timestamp")}'


class InfluxSource(InfluxScript):
    QUERY_GET_DATA = "{select_from}+WHERE+{TIMESTAMP_CONDITION}+{where}"

    def get_config(self) -> dict:
        return {
            'conf.resourceUrl': urljoin(
                self.pipeline.source.config['host'],
                f'/query?db={self.pipeline.source.config["db"]}&epoch=ms&q={self.get_query()}'
            ),
            **self.get_auth_config()
        }

    def get_auth_config(self):
        if 'username' not in self.pipeline.source.config:
            return {}
        return {
            'conf.client.authType': 'BASIC',
            'conf.client.basicAuth.username': self.pipeline.source.config['username'],
            'conf.client.basicAuth.password': self.pipeline.source.config.get('password', '')
        }

    def get_query(self) -> str:
        # build common statements
        delay = self.pipeline.config.get('delay', '0s')
        interval = str(self.pipeline.config.get('interval', 60)) + 's'
        timestamp_condition = self._get_timestamp_condition(interval, delay)

        if self.pipeline.query:
            select_from = quote_plus(re.split('where', self.pipeline.query, flags=re.IGNORECASE)[0].strip())
            if TIMESTAMP_CONDITION not in self.pipeline.query:
                raise ValueError(f'Pipeline "{self.pipeline.name}" has misconfiguration in a query'
                                 f'{TIMESTAMP_CONDITION} is absent')
            where = self.pipeline.query.split(TIMESTAMP_CONDITION)[-1].strip()
            where = f'{quote_plus(where)}' if where else ''
        else:
            dimensions_to_select = [f'"{d}"::tag' for d in self.pipeline.dimension_paths]
            values_to_select = ['*::field' if v == '*' else f'"{v}"::field' for v in self.pipeline.value_paths]
            columns = quote_plus(','.join(dimensions_to_select + values_to_select))

            where = self.pipeline.config.get('filtering')
            where = f'AND+%28{quote_plus(where)}%29' if where else ''

            measurement_name = self.pipeline.config['measurement_name']
            if '.' not in measurement_name and ' ' not in measurement_name:
                measurement_name = f'%22{measurement_name}%22'
            select_from = "SELECT+{dimensions}+FROM+{metric}".format(**{'dimensions': columns, 'metric': measurement_name})

        return self.QUERY_GET_DATA.format(
            **{
                'select_from': select_from,
                'TIMESTAMP_CONDITION': timestamp_condition,
                'where': where
            }
        )

    def _get_timestamp_condition(self, interval, delay) -> str:
        return f"%28%22time%22+%3E%3D+{LAST_TIMESTAMP}+AND+%22time%22+%3C+{LAST_TIMESTAMP}%2B{interval}+AND+%22time%22+%3C+now%28%29+-+{delay}%29"


class TestInfluxSource(JythonSource):
    JYTHON_SCRIPT = 'influx.py'
    JYTHON_SCRIPTS_DIR = os.path.join(JythonSource.JYTHON_SCRIPTS_DIR, 'test_pipelines')

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'USERNAME',
                'value': self.pipeline.source.config.get('username', 'root')
            },
            {
                'key': 'PASSWORD',
                'value': self.pipeline.source.config.get('password', 'root')
            },
            {
                'key': 'DATABASE',
                'value': self.pipeline.source.config.get('db')
            },
            {
                'key': 'HOST',
                'value': self.pipeline.source.config.get('host')
            },
            {
                'key': 'REQUEST_TIMEOUT',
                'value': 10
            },
        ]
