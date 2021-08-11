from agent import pipeline
from urllib.parse import urljoin, quote_plus
from agent.pipeline.config.stages.influx import InfluxScript

# todo
FLUX = 'Flux'
INFLUXQL = 'InfluxQL'


class Influx2Source(InfluxScript):
    JYTHON_SCRIPT = 'influx2.py'
    # todo duplicate
    QUERY_GET_DATA = "SELECT+{dimensions}+FROM+{metric}+WHERE+%28%22time%22+%3E%3D+${{record:value('/last_timestamp')}}+AND+%22time%22+%3C+${{record:value('/last_timestamp')}}%2B{interval}+AND+%22time%22+%3C+now%28%29+-+{delay}%29+{where}"

    def get_config(self) -> dict:
        config = super().get_config()
        config['scriptConf.params'].extend([
            {'key': 'URL', 'value': self._get_url()},
            {'key': 'HEADERS', 'value': self._get_headers()},
            {'key': 'DATA', 'value': self._get_data()},
        ])
        return config

    def _get_url(self) -> str:
        if self.pipeline.config['query_type'] == FLUX:
            path = f'/api/v2/query?org={self.pipeline.source.config["org"]}'
        else:
            # todo do I need epoch
            path = f'/query?org={self.pipeline.source.config["org"]}database={self.pipeline.source.config["db"]}&epoch=ms'
        return urljoin(self.pipeline.source.config['host'], path)

    def _get_headers(self) -> dict:
        headers = {
            'Authorization': f'Token {self.pipeline.source.config["token"]}',
            'Accept': 'application/csv',
        }
        if self.pipeline.config['query_type'] == INFLUXQL:
            return {**headers, 'Content-type': 'application/json'}
        return {**headers, 'Content-type': 'application/vnd.flux'}

    def _get_data(self) -> str:
        if self.pipeline.config['query_type'] == INFLUXQL:
            return self._get_influxql_query()
        return f'from(bucket:"{self.pipeline.source.config["bucket"]}") ' \
               '|> range(start: {}, stop: {}) ' \
               f'|> filter(fn: (r) => r._measurement == "{self.pipeline.config["measurement_name"]}")'

    # todo duplicate
    def _get_influxql_query(self) -> str:
        if isinstance(self.pipeline, pipeline.TestPipeline):
            return f'select+%2A+from+{self.pipeline.config["measurement_name"]}+limit+{pipeline.manager.MAX_SAMPLE_RECORDS}'

        dimensions_to_select = [f'"{d}"::tag' for d in self.pipeline.dimensions_names]
        values_to_select = ['*::field' if v == '*' else f'"{v}"::field' for v in self.pipeline.value_names]
        delay = self.pipeline.config.get('delay', '0s')
        columns = quote_plus(','.join(dimensions_to_select + values_to_select))

        where = self.pipeline.config.get('filtering')
        where = f'AND+%28{quote_plus(where)}%29' if where else ''

        measurement_name = self.pipeline.config['measurement_name']
        if '.' not in measurement_name and ' ' not in measurement_name:
            measurement_name = f'%22{measurement_name}%22'

        return self.QUERY_GET_DATA.format(**{
            'dimensions': columns,
            'metric': measurement_name,
            'delay': delay,
            'interval': str(self.pipeline.config.get('interval', 60)) + 's',
            'where': where
        })
