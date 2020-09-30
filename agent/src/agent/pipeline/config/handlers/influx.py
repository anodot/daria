import json

from . import base
from agent.modules.logger import get_logger
from agent.modules.constants import HOSTNAME
from urllib.parse import urljoin, quote_plus
from agent.pipeline.config import stages

logger = get_logger(__name__)


class InfluxConfigHandler(base.BaseConfigHandler):
    stages_to_override = {
        'source': stages.influx_source.InfluxScript,
    }

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

    QUERY_GET_DATA = "SELECT+{dimensions}+FROM+{metric}+WHERE+%28%22time%22+%3E%3D+${{record:value('/last_timestamp')}}+AND+%22time%22+%3C+${{record:value('/last_timestamp')}}%2B{interval}+AND+%22time%22+%3C+now%28%29+-+{delay}%29+{where}"

    def override_stages(self):
        super().override_stages()
        self.update_source_configs()
        required = [self.replace_illegal_chars(d) for d in self.pipeline.config['dimensions']['required']]
        optional = [self.replace_illegal_chars(d) for d in self.pipeline.config['dimensions']['optional']]

        for stage in self.config['stages']:
            if stage['instanceName'] == 'transform_records':
                for conf in stage['configuration']:
                    if conf['name'] == 'stageRequiredFields':
                        conf['value'] = ['/' + d for d in required]

                    if conf['name'] == 'initScript':
                        conf['value'] = self.DECLARE_VARS_JS.format(
                            required_dimensions=str(required),
                            optional_dimensions=str(optional),
                            measurement_name=self.replace_illegal_chars(self.pipeline.config['measurement_name']),
                            target_type=self.pipeline.config.get('target_type', 'gauge'),
                            constant_properties=str(self.pipeline.constant_dimensions),
                            host_id=self.pipeline.destination.host_id,
                            host_name=HOSTNAME,
                            pipeline_id=self.pipeline.name,
                            tags=json.dumps(self.pipeline.get_tags())
                        )
            if stage['instanceName'] == 'destination':
                for conf in stage['configuration']:
                    if conf['name'] in self.pipeline.destination.config:
                        conf['value'] = self.pipeline.destination.config[conf['name']]

    def update_source_configs(self):
        source_config = self.pipeline.source.config
        dimensions_to_select = [f'"{d}"::tag' for d in self.pipeline.dimensions_names]
        values_to_select = ['*::field' if v == '*' else f'"{v}"::field' for v in self.pipeline.config['value']['values']]
        username = source_config.get('username', '')
        password = source_config.get('password', '')
        if username != '':
            self.pipeline.source.config['conf.client.authType'] = 'BASIC'
            self.pipeline.source.config['conf.client.basicAuth.username'] = username
            self.pipeline.source.config['conf.client.basicAuth.password'] = password

        delay = self.pipeline.config.get('delay', '0s')
        columns = quote_plus(','.join(dimensions_to_select + values_to_select))

        where = self.pipeline.config.get('filtering')
        where = f'AND+%28{quote_plus(where)}%29' if where else ''

        measurement_name = self.pipeline.config['measurement_name']
        if '.' not in measurement_name and ' ' not in measurement_name:
            measurement_name = f'%22{measurement_name}%22'

        for stage in self.config['stages']:
            if stage['instanceName'] == 'get_interval_records':
                query = f"/query?db={source_config['db']}&epoch=ms&q={self.QUERY_GET_DATA}".format(**{
                    'dimensions': columns,
                    'metric': measurement_name,
                    'delay': delay,
                    # interval is in minutes
                    'interval': str(int(self.pipeline.config.get('interval', 60) * 60)) + 's',
                    'where': where
                })
                self.update_http_stage(stage, self.pipeline.source.config, urljoin(source_config['host'], query))

    @staticmethod
    def replace_illegal_chars(string: str) -> str:
        return string.replace(' ', '_').replace('.', '_').replace('<', '_')

    @staticmethod
    def update_http_stage(stage, config, url=None):
        for conf in stage['configuration']:
            if conf['name'] == 'conf.resourceUrl' and url:
                conf['value'] = url
                continue

            if conf['name'] in config:
                conf['value'] = config[conf['name']]
