import csv

from .expression_parser import condition
from .base import BaseConfigHandler
from agent.logger import get_logger

logger = get_logger(__name__)


class SchemalessConfigHandler(BaseConfigHandler):
    DECLARE_VARS_JS = """/*
state['TIMESTAMP_COLUMN'] = 'timestamp_unix';
state['DIMENSIONS'] = ['ver', 'AdSize', 'Country', 'AdType', 'Exchange'];
state['VALUES_COLUMNS'] = ['Clicks', 'Impressions'];
state['MEASUREMENT_NAMES'] = ['clicks', 'impressions'];
state['TARGET_TYPES'] = ['gauge', 'counter']
state['COUNT_RECORDS'] = 1
*/

state['TIMESTAMP_COLUMN'] = '{timestamp_column}';
state['DIMENSIONS'] = {dimensions};
state['DIMENSIONS_NAMES'] = {dimensions_names};
state['VALUES_COLUMNS'] = {values};
state['MEASUREMENT_NAMES'] = {measurement_names};
state['TARGET_TYPES'] = {target_types};
state['COUNT_RECORDS'] = {count_records};
state['COUNT_RECORDS_MEASUREMENT_NAME'] = '{count_records_measurement_name}';
state['STATIC_WHAT'] = {static_what};
state['metrics'] = {{}}
"""

    def override_stages(self):
        self.update_source_configs()

        self.update_stages()

        self.update_destination_config()

    def update_stages(self):
        for stage in self.config['stages']:
            if stage['instanceName'] == 'JavaScriptEvaluator_01':
                self.set_variables_js(stage)

            if stage['instanceName'] == 'ExpressionEvaluator_02':
                self.set_constant_properties(stage)
                self.convert_timestamp_to_unix(stage)

            if stage['instanceName'] == 'ExpressionEvaluator_03':
                self.set_preconditions(stage)
                self.check_dimensions(stage)

    def get_measurement_names(self) -> list:
        measurement_names = []
        for key in self.client_config['values'].keys():
            if key in self.client_config['measurement_names']:
                measurement_names.append(self.get_property_mapping(self.client_config['measurement_names'][key]))
            else:
                measurement_names.append(key)
        return measurement_names

    def check_dimensions(self, stage):
        for conf in stage['configuration']:
            if conf['name'] != 'expressionProcessorConfigs':
                continue
            dimensions = self.client_config['dimensions']['required'] + self.client_config['dimensions']['optional']
            for d in dimensions:
                d_path = self.get_property_mapping(d)
                conf['value'].append({
                    'fieldToSet': f'/{d_path}',
                    'expression': '${' + f"record:exists('/{d_path}') ? (record:value('/{d_path}') == null) ? 'NULL' : record:value('/{d_path}') : null" + '}'
                })

            conf['value'] += self.get_transformations()

    def get_transformations(self):
        transformations = []
        file = self.client_config.get('transform', {}).get('file')
        if not file:
            return transformations
        with open(file) as f:
            for row in csv.DictReader(f, fieldnames=['result', 'value', 'condition']):
                exp = f"'{row['value']}'"
                if row['condition']:
                    exp = f"{condition.get_expression(row['condition'])} ? {exp} : record:value('/{row['result']}')"

                transformations.append({'fieldToSet': '/' + row['result'], 'expression': '${' + exp + '}'})
        return transformations

    def set_variables_js(self, stage):
        for conf in stage['configuration']:
            if conf['name'] == 'initScript':
                dimensions_names = self.client_config['dimensions']['required'] + self.client_config['dimensions']['optional']
                conf['value'] = self.DECLARE_VARS_JS.format(
                    timestamp_column=str(self.get_property_mapping(self.client_config['timestamp']['name'])),
                    dimensions=[self.get_property_mapping(value) for value in dimensions_names],
                    dimensions_names=dimensions_names,
                    values=str(list([self.get_property_mapping(value) for value in self.client_config['values'].keys()])),
                    target_types=str(list([self.get_property_mapping(value) for value in self.client_config['values'].values()])),
                    measurement_names=str(list(self.get_measurement_names())),
                    count_records=int(self.client_config.get('count_records', False)),
                    count_records_measurement_name=str(
                        self.client_config.get('count_records_measurement_name', 'count')),
                    static_what=int(self.client_config.get('static_what', True)),
                )

    def set_preconditions(self, stage):
        for conf in stage['configuration']:
            if conf['name'] == 'stageRequiredFields':
                conf['value'] = ['/' + self.get_property_mapping(d) for d in self.client_config['dimensions']['required']]
                for value in self.client_config['values'].keys():
                    conf['value'].append('/' + self.get_property_mapping(value))
                if self.client_config['timestamp']['name'] != 'kafka_timestamp':
                    conf['value'].append('/' + self.get_property_mapping(self.client_config['timestamp']['name']))
                if not self.client_config.get('static_what', True):
                    for value in list(self.client_config['measurement_names'].values()) + list(self.client_config['values'].values()):
                        conf['value'].append('/' + self.get_property_mapping(value))
            if conf['name'] == 'stageRecordPreconditions':
                conf['value'] = []
                if self.client_config.get('filter', {}).get('condition'):
                    conf['value'].append('${' + condition.get_expression(
                        self.client_config['filter']['condition']) + '}')