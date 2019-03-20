from .base import BaseConfigHandler
from agent.logger import get_logger

logger = get_logger(__name__)


class InfluxConfigHandler(BaseConfigHandler):
    def override_stages(self):
        dimensions = self.get_dimensions()
        source_config = self.client_config['source']['config']
        source_config['conf.resourceUrl'] = source_config['conf.resourceUrl'].format(
            dimensions=','.join(dimensions + self.client_config['value']['values']),
            metric=self.client_config['measurement_name'],
            startAt='{startAt}'
        )
        self.update_source_configs()

        for stage in self.config['stages']:
            if stage['instanceName'] != 'JavaScriptEvaluator_02':
                continue

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

        self.update_destination_config()
