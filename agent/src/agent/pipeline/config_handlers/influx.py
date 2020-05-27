import json

from .base import BaseConfigHandler, ConfigHandlerException
from ...logger import get_logger
from ...constants import HOSTNAME
from datetime import datetime, timedelta
from influxdb import InfluxDBClient
from urllib.parse import urljoin, urlparse, quote_plus

logger = get_logger(__name__)


class InfluxConfigHandler(BaseConfigHandler):
    DECLARE_VARS_JS = """/*
state['MEASUREMENT_NAME'] = 'clicks';
state['REQUIRED_DIMENSIONS'] = ['AdType', 'Exchange'];
state['OPTIONAL_DIMENSIONS'] = ['ver', 'AdSize', 'Country'];
state['VALUES_COLUMNS'] = ['value'];
state['TARGET_TYPE'] = 'gauge';
state['VALUE_CONSTANT'] = 1
state['HOST_ID'] = 'acgdhjehfje'
*/

state['MEASUREMENT_NAME'] = '{measurement_name}';
state['REQUIRED_DIMENSIONS'] = {required_dimensions};
state['OPTIONAL_DIMENSIONS'] = {optional_dimensions};
state['TARGET_TYPE'] = '{target_type}';
state['CONSTANT_PROPERTIES'] = {constant_properties}
state['HOST_ID'] = '{host_id}'
state['HOST_NAME'] = '{host_name}'
state['PIPELINE_ID'] = '{pipeline_id}'
state['TAGS'] = {tags}
"""
    PIPELINE_BASE_CONFIG_NAME = 'influx_http.json'

    QUERY_GET_DATA = "SELECT+{dimensions}+FROM+%22{metric}%22+WHERE+%28%22time%22+%3E%3D+${{record:value('/last_timestamp')}}+AND+%22time%22+%3C+${{record:value('/last_timestamp')}}%2B{interval}+AND+%22time%22+%3C+now%28%29-{delay}%29+{where}"
    QUERY_GET_TIMESTAMP = "SELECT+last_timestamp+FROM+agent_timestamps+WHERE+pipeline_id%3D%27${pipeline:id()}%27+ORDER+BY+time+DESC+LIMIT+1"
    QUERY_CHECK_DATA = "SELECT+{dimensions}+FROM+%22{metric}%22+WHERE+%28%22time%22+%3E+${{record:value('/last_timestamp_value')}}+AND+%22time%22+%3C+now%28%29-{delay}%29+{where}+ORDER+BY+time+ASC+limit+1"

    def get_write_client(self):
        host, db, username, password = self.get_write_config()
        influx_url_parsed = urlparse(host)
        influx_url = influx_url_parsed.netloc.split(':')
        args = {'database': db, 'host': influx_url[0], 'port': influx_url[1]}
        if username != '':
            args['username'] = username
            args['password'] = password
        if influx_url_parsed.scheme == 'https':
            args['ssl'] = True
        return InfluxDBClient(**args)

    def get_write_config(self):
        source_config = self.pipeline.source.config
        if 'write_host' in source_config:
            host = source_config['write_host']
            db = source_config['write_db']
            username = source_config.get('write_username', '')
            password = source_config.get('write_password', '')
        else:
            host = source_config['host']
            db = source_config['db']
            username = source_config.get('username', '')
            password = source_config.get('password', '')
        return host, db, username, password

    def set_write_config_pipeline(self):
        host, db, username, password = self.get_write_config()
        config = {'host': host, 'db': db}
        if username != '':
            config['conf.client.authType'] = 'BASIC'
            config['conf.client.basicAuth.username'] = username
            config['conf.client.basicAuth.password'] = password
        return config

    def set_initial_offset(self, client_config=None):
        if client_config:
            self.client_config = client_config
        source_config = self.pipeline.source.config
        if not source_config.get('offset'):
            source_config['offset'] = '0'

        if str(source_config['offset']).isdigit():
            timestamp = datetime.now() - timedelta(days=int(source_config['offset']))
        else:
            timestamp = datetime.strptime(source_config['offset'], '%d/%m/%Y %H:%M')

        source_config['offset'] = int(timestamp.timestamp() * 1e9)

        self.get_write_client().write_points([{
            'measurement': 'agent_timestamps',
            'tags': {'pipeline_id': self.client_config['pipeline_id']},
            'fields': {'last_timestamp': source_config['offset']}
        }])

    def replace_illegal_chars(self, string: str) -> str:
        return string.replace(' ', '_').replace('.', '_').replace('<', '_')

    def override_stages(self):

        self.update_source_configs()
        required = [self.replace_illegal_chars(d) for d in self.client_config['dimensions']['required']]
        optional = [self.replace_illegal_chars(d) for d in self.client_config['dimensions']['optional']]

        for stage in self.config['stages']:
            if stage['instanceName'] == 'transform_records':
                for conf in stage['configuration']:
                    if conf['name'] == 'stageRequiredFields':
                        conf['value'] = ['/' + d for d in required]

                    if conf['name'] == 'initScript':
                        conf['value'] = self.DECLARE_VARS_JS.format(
                            required_dimensions=str(required),
                            optional_dimensions=str(optional),
                            measurement_name=self.replace_illegal_chars(self.client_config['measurement_name']),
                            target_type=self.client_config.get('target_type', 'gauge'),
                            constant_properties=str(self.pipeline.constant_dimensions),
                            host_id=self.pipeline.destination.host_id,
                            host_name=HOSTNAME,
                            pipeline_id=self.pipeline.id,
                            tags=json.dumps(self.get_tags())
                        )

        self.update_destination_config()

    def update_source_configs(self):

        dimensions = self.get_dimensions()
        source_config = self.pipeline.source.config
        dimensions_to_select = [f'"{d}"::tag' for d in dimensions]
        values_to_select = ['*::field' if v == '*' else f'"{v}"::field' for v in self.client_config['value']['values']]
        username = source_config.get('username', '')
        password = source_config.get('password', '')
        if username != '':
            self.pipeline.source.config['conf.client.authType'] = 'BASIC'
            self.pipeline.source.config['conf.client.basicAuth.username'] = username
            self.pipeline.source.config['conf.client.basicAuth.password'] = password

        delay = self.client_config.get('delay', '0s')
        interval = self.client_config.get('interval', 60)
        columns = quote_plus(','.join(dimensions_to_select + values_to_select))
        self.set_initial_offset()

        write_config = self.set_write_config_pipeline()
        write_config['conf.spoolingPeriod'] = interval
        write_config['conf.poolingTimeoutSecs'] = interval

        where = self.client_config.get('filtering')
        where = f'AND+%28{quote_plus(where)}%29' if where else ''

        for stage in self.config['stages']:
            if stage['instanceName'] == 'get_interval_records':
                query = f"/query?db={source_config['db']}&epoch=ms&q={self.QUERY_GET_DATA}".format(**{
                    'dimensions': columns,
                    'metric': self.client_config['measurement_name'],
                    'delay': delay,
                    'interval': str(interval) + 's',
                    'where': where
                })
                self.update_http_stage(stage, self.pipeline.source.config, urljoin(source_config['host'], query))

            if stage['instanceName'] == 'get_last_agent_timestamp':
                get_timestamp_url = urljoin(write_config['host'],
                                            f"/query?db={write_config['db']}&epoch=ns&q={self.QUERY_GET_TIMESTAMP}")
                self.update_http_stage(stage, write_config, get_timestamp_url)

            if stage['instanceName'] == 'save_next_record_timestamp':
                self.update_http_stage(stage, write_config, urljoin(write_config['host'],
                                                      f"/write?db={write_config['db']}&precision=ns"))

            if stage['instanceName'] == 'get_next_record_timestamp':
                query = f"/query?db={source_config['db']}&epoch=ns&q={self.QUERY_CHECK_DATA}".format(**{
                    'dimensions': columns,
                    'metric': self.client_config['measurement_name'],
                    'delay': delay,
                    'where': where
                })
                self.update_http_stage(stage, self.pipeline.source.config, urljoin(source_config['host'], query))

    def update_http_stage(self, stage, config, url=None):
        for conf in stage['configuration']:
            if conf['name'] == 'conf.resourceUrl' and url:
                conf['value'] = url
                continue

            if conf['name'] in config:
                conf['value'] = config[conf['name']]
