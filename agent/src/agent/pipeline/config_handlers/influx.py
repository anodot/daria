import os

from .base import BaseConfigHandler, ConfigHandlerException
from agent.constants import SDC_DATA_PATH
from agent.logger import get_logger
from datetime import datetime, timedelta
from urllib.parse import urljoin

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

    DB_QUERY = "SELECT+{dimensions}+FROM+{metric}+WHERE+time+%3E+${{record:value('/text')}}+LIMIT+{limit}"

    def set_initial_offset(self):
        source_config = self.client_config['source']['config']
        if not source_config['offset']:
            source_config['offset'] = 0
        else:
            if source_config['offset'].isdigit():
                timestamp = datetime.now() - timedelta(days=int(source_config['offset']))
            else:
                timestamp = datetime.strptime(source_config['offset'], '%d/%m/%Y %H:%M')

            source_config['offset'] = int(timestamp.timestamp() * 1e9)

        offset_file_dir = os.path.join(SDC_DATA_PATH, 'timestamps', self.client_config['pipeline_id'])
        offset_file_path = os.path.join(offset_file_dir, 'timestamp_')
        if not os.path.isdir(offset_file_dir):
            os.makedirs(offset_file_dir)
            os.chmod(offset_file_dir, 0o777)

            with open(offset_file_path, 'w+') as f:
                f.write(str(source_config['offset']))

    def override_stages(self):
        dimensions = self.get_dimensions()
        source_config = self.client_config['source']['config']
        columns_to_select = dimensions + self.client_config['value']['values']

        self.set_initial_offset()
        query = f"/query?db={source_config['db']}&epoch=ns&q={self.DB_QUERY}".format(**{
            'dimensions': ','.join(columns_to_select),
            'metric': self.client_config['measurement_name'],
            'limit': source_config['limit']
        })
        source_config['conf.resourceUrl'] = urljoin(source_config['host'], query)

        for stage in self.config['stages']:
            if stage['instanceName'] == 'HTTPClient_03':
                for conf in stage['configuration']:
                    if conf['name'] in self.client_config['source']['config']:
                        conf['value'] = self.client_config['source']['config'][conf['name']]

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
                        for d in self.client_config['dimensions']['required']:
                            conf['value'].append(f"${{record:type('/{d}') == 'STRING'}}")
                        for d in self.client_config['dimensions']['optional']:
                            conf['value'].append(f"${{record:type('/{d}') == 'STRING' or record:type('/{d}') == NULL}}")
                        for v in self.client_config['value']['values']:
                            conf['value'].append(f"${{record:type('/{v}') != 'STRING'}}")

            if stage['instanceName'] == 'ExpressionEvaluator_01':
                for conf in stage['configuration']:
                    if conf['name'] == 'expressionProcessorConfigs':
                        for key, val in self.client_config.get('properties', {}).items():
                            conf['value'].append({'fieldToSet': '/properties/' + key, 'expression': val})

        self.update_destination_config()
