import json

from . import base
from agent.modules.logger import get_logger
from agent.modules.constants import HOSTNAME
from urllib.parse import urljoin, quote_plus
from agent.pipeline.config import stages
from ... import pipeline

logger = get_logger(__name__)


class InfluxConfigHandler(base.BaseConfigHandler):
    stages_to_override = {
        'source': stages.influx_source.InfluxScript,
        'destination': stages.destination.Destination
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
    QUERY_GET_DATA = "SELECT+{dimensions}+FROM+{metric}+WHERE+%28%22time%22+%3E%3D+${{record:value('/last_timestamp')}}+AND+%22time%22+%3C+${{record:value('/last_timestamp')}}%2B{interval}+AND+%22time%22+%3C+now%28%29+-+{delay}%29+{where}"

    def _override_stages(self):
        super()._override_stages()
        self.update_source_configs()

        for stage in self.config['stages']:
            if stage['instanceName'] == 'transform_records':
                for conf in stage['configuration']:
                    if conf['name'] == 'stageRequiredFields':
                        conf['value'] = ['/' + d for d in self.get_required_dimensions()]

                    if conf['name'] == 'initScript':
                        conf['value'] = self.DECLARE_VARS_JS.format(
                            required_dimensions=str(self.get_required_dimensions()),
                            optional_dimensions=str(self.get_optional_dimensions()),
                            measurement_name=self.replace_illegal_chars(self.pipeline.config['measurement_name']),
                            target_type=self.pipeline.config.get('target_type', 'gauge'),
                            constant_properties=str(self.pipeline.constant_dimensions),
                            host_id=self.pipeline.destination.host_id,
                            host_name=HOSTNAME,
                            pipeline_id=self.pipeline.name,
                            tags=json.dumps(self.pipeline.get_tags())
                        )

    def get_required_dimensions(self):
        return [self.replace_illegal_chars(d) for d in self.pipeline.config['dimensions']['required']]

    def get_optional_dimensions(self):
        return [self.replace_illegal_chars(d) for d in self.pipeline.config['dimensions'].get('optional', [])]

    def update_source_configs(self):
        source_config = self.pipeline.source.config
        username = source_config.get('username', '')
        password = source_config.get('password', '')
        if username != '':
            self.pipeline.source.config['conf.client.authType'] = 'BASIC'
            self.pipeline.source.config['conf.client.basicAuth.username'] = username
            self.pipeline.source.config['conf.client.basicAuth.password'] = password

        for stage in self.config['stages']:
            if stage['instanceName'] == 'get_interval_records':
                for conf in stage['configuration']:
                    if conf['name'] == 'conf.resourceUrl':
                        params = f"/query?db={source_config['db']}&epoch=ms&q="
                        conf['value'] = urljoin(source_config['host'], params + self.get_query())
                        continue

                    if conf['name'] in source_config:
                        conf['value'] = source_config[conf['name']]

    def get_query(self):
        if self.is_preview:
            return f"select+%2A+from+{self.config['measurement_name']}+limit+{pipeline.manager.MAX_SAMPLE_RECORDS}"

        dimensions_to_select = [f'"{d}"::tag' for d in self.pipeline.dimensions_names]
        values_to_select = ['*::field' if v == '*' else f'"{v}"::field' for v in
                            self.pipeline.config['value']['values']]
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

    @staticmethod
    def replace_illegal_chars(string: str) -> str:
        return string.replace(' ', '_').replace('.', '_').replace('<', '_')
