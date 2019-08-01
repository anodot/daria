import os

from .base import BaseConfigHandler, ConfigHandlerException
from agent.logger import get_logger
from datetime import datetime, timedelta
from influxdb import InfluxDBClient
from urllib.parse import urljoin, urlparse

logger = get_logger(__name__)


class InfluxConfigHandler(BaseConfigHandler):
    DECLARE_VARS_JS = """/*
state['MEASUREMENT_NAME'] = 'clicks';
state['REQUIRED_DIMENSIONS'] = ['AdType', 'Exchange'];
state['OPTIONAL_DIMENSIONS'] = ['ver', 'AdSize', 'Country'];
state['VALUES_COLUMNS'] = ['value'];
state['TARGET_TYPE'] = 'gauge';
state['VALUE_CONSTANT'] = 1
*/

state['MEASUREMENT_NAME'] = '{measurement_name}';
state['REQUIRED_DIMENSIONS'] = {required_dimensions};
state['OPTIONAL_DIMENSIONS'] = {optional_dimensions};
state['VALUES_COLUMNS'] = {values};
state['TARGET_TYPE'] = '{target_type}';
state['VALUE_CONSTANT'] = {value_constant}
"""

    QUERY_GET_DATA = "SELECT+{dimensions}+FROM+%22{metric}%22+WHERE+%22time%22+%3E+${{record:value('/last_timestamp')}}+LIMIT+{limit}"
    QUERY_GET_TIMESTAMP = "SELECT+last_timestamp+FROM+agent_timestamps+WHERE+pipeline_id%3D%27${pipeline:id()}%27+ORDER+BY+time+DESC+LIMIT+1"

    def set_initial_offset(self):
        source_config = self.client_config['source']['config']
        if not source_config['offset']:
            source_config['offset'] = '0'

        if source_config['offset'].isdigit():
            timestamp = datetime.now() - timedelta(days=int(source_config['offset']))
        else:
            timestamp = datetime.strptime(source_config['offset'], '%d/%m/%Y %H:%M')

        source_config['offset'] = int(timestamp.timestamp() * 1e9)

        influx_url = urlparse(source_config['host']).netloc.split(':')
        client = InfluxDBClient(influx_url[0], influx_url[1], database=source_config['db'])
        client.write_points([{
            'measurement': 'agent_timestamps',
            'tags': {'pipeline_id': self.client_config['pipeline_id']},
            'fields': {'last_timestamp': source_config['offset']}
        }])

    def override_stages(self):

        self.update_source_configs()

        source_config = self.client_config['source']['config']
        for stage in self.config['stages']:

            if stage['instanceName'] == 'JavaScriptEvaluator_02':
                for conf in stage['configuration']:
                    if conf['name'] == 'stageRequiredFields':
                        conf['value'] = ['/' + d for d in self.client_config['dimensions']['required']]

                    if conf['name'] == 'initScript':
                        conf['value'] = self.DECLARE_VARS_JS.format(
                            required_dimensions=str(self.client_config['dimensions']['required']),
                            optional_dimensions=str(self.client_config['dimensions']['optional']),
                            measurement_name=self.client_config['measurement_name'],
                            values=str(self.client_config['value'].get('values', [])),
                            target_type=self.client_config.get('target_type', 'gauge'),
                            value_constant=self.client_config['value'].get('constant', '1')
                        )

                    if conf['name'] == 'stageRecordPreconditions':
                        conf['value'] = []
                        for d in self.client_config['dimensions']['required']:
                            conf['value'].append(f"${{record:type('/{d}') == 'STRING'}}")
                        for d in self.client_config['dimensions']['optional']:
                            conf['value'].append(f"${{record:type('/{d}') == 'STRING' or record:type('/{d}') == NULL}}")
                        for v in self.client_config['value']['values']:
                            conf['value'].append(f"${{record:type('/{v}') != 'STRING'}}")

            if stage['instanceName'] == 'ExpressionEvaluator_01':
                self.set_constant_properties(stage)

            if stage['instanceName'] == 'HTTPClient_05':
                for conf in stage['configuration']:
                    if conf['name'] == 'conf.resourceUrl':
                        conf['value'] = urljoin(source_config['host'],
                                                f"/write?db={source_config['db']}&precision=ns")

        self.update_destination_config()

    def update_source_configs(self):

        dimensions = self.get_dimensions()
        source_config = self.client_config['source']['config']
        dimensions_to_select = [f'%22{d}%22' + '%3A%3Atag' for d in dimensions]
        values_to_select = [f'%22{v}%22' + '%3A%3Afield' for v in self.client_config['value']['values']]

        self.set_initial_offset()
        query = f"/query?db={source_config['db']}&epoch=ns&q={self.QUERY_GET_DATA}".format(**{
            'dimensions': ','.join(dimensions_to_select + values_to_select),
            'metric': self.client_config['measurement_name'],
            'limit': source_config['limit']
        })
        source_config['conf.resourceUrl'] = urljoin(source_config['host'], query)

        get_timestamp_url = urljoin(source_config['host'],
                                    f"/query?db={source_config['db']}&epoch=ns&q={self.QUERY_GET_TIMESTAMP}")

        for stage in self.config['stages']:
            if stage['instanceName'] == 'HTTPClient_03':
                for conf in stage['configuration']:
                    if conf['name'] in self.client_config['source']['config']:
                        conf['value'] = self.client_config['source']['config'][conf['name']]

            if stage['instanceName'] == 'HTTPClient_04':
                for conf in stage['configuration']:
                    if conf['name'] == 'conf.resourceUrl':
                        conf['value'] = get_timestamp_url
