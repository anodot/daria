import requests

from .base import BaseConfigHandler, ConfigHandlerException
from agent.logger import get_logger
from datetime import datetime, timedelta
from urllib.parse import urljoin

logger = get_logger(__name__)


class InfluxConfigHandler(BaseConfigHandler):

    def set_initial_offset(self, query):
        source_config = self.client_config['source']['config']
        if not source_config['conf.pagination.startAt']:
            source_config['conf.pagination.startAt'] = 0
            return

        if source_config['conf.pagination.startAt'].isdigit():
            timestamp = datetime.now() - timedelta(days=int(source_config['conf.pagination.startAt']))
        else:
            timestamp = datetime.strptime(source_config['conf.pagination.startAt'], '%d/%m/%Y %H:%M')

        try:
            query = 'SELECT count(*) FROM ({query} WHERE time < {time})'.format(**{
                'query': query,
                'time': int(timestamp.timestamp() * 1e9)
            })
            source_config['conf.pagination.startAt'] = requests.get(urljoin(source_config['conf.resourceUrl']['host'],
                                                                            '/query'), params={
                'db': source_config['conf.resourceUrl']['db'],
                'q': query
            }).json()['results'][0]['series'][0]['values'][0][1]
        except requests.exceptions.ConnectionError:
            raise ConfigHandlerException('Failed to connect to source api url')
        except KeyError:
            source_config['conf.pagination.startAt'] = 0

    def override_stages(self):
        dimensions = self.get_dimensions()
        source_config = self.client_config['source']['config']
        columns_to_select = dimensions + self.client_config['value']['values']
        query_start = 'SELECT {dimensions} FROM {metric}'.format(**{
            'dimensions': ','.join(columns_to_select),
            'metric': self.client_config['measurement_name'],
        })
        self.set_initial_offset(query_start)
        query = '/query?db={db}&epoch=s&q={query}+LIMIT+{limit}+OFFSET+${startAt}'.format(**{
            'query': query_start.replace(' ', '+'),
            'startAt': '{startAt}',
            **source_config['conf.resourceUrl']
        })
        source_config['conf.resourceUrl'] = urljoin(source_config['conf.resourceUrl']['host'], query)
        self.update_source_configs()

        for stage in self.config['stages']:
            if stage['instanceName'] == 'JavaScriptEvaluator_01':
                for conf in stage['configuration']:
                    if conf['name'] == 'initScript':
                        conf['value'] = conf['value'].format(columns=str(['time'] + columns_to_select))

            if stage['instanceName'] == 'JavaScriptEvaluator_02':
                for conf in stage['configuration']:
                    if conf['name'] == 'stageRequiredFields':
                        conf['value'] = ['/' + d for d in self.client_config['dimensions']['required']]

                    if conf['name'] == 'initScript':
                        conf['value'] = conf['value'].format(
                            required_dimensions=str(self.client_config['dimensions']['required']),
                            optional_dimensions=str(self.client_config['dimensions']['optional']),
                            measurement_name=self.client_config['measurement_name'],
                            values=str(self.client_config['value']['values']),
                            target_type=self.client_config['target_type'],
                            value_constant=self.client_config['value']['constant']
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
                        for key, val in self.client_config['properties'].items():
                            conf['value'].append({'fieldToSet': '/properties/' + key, 'expression': val})

        self.update_destination_config()
