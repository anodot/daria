import json

from . import base
from agent.modules.logger import get_logger
from agent.modules.constants import HOSTNAME
from urllib.parse import urljoin, quote_plus
from agent.pipeline.config import stages
from agent import pipeline

logger = get_logger(__name__)


class InfluxConfigHandler(base.BaseConfigHandler):
    stages_to_override = {
        'offset': stages.influx_offset.InfluxScript,
        'source': stages.influx_source.InfluxSource,
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

    def _override_stages(self):
        super()._override_stages()

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

    @staticmethod
    def replace_illegal_chars(string: str) -> str:
        return string.replace(' ', '_').replace('.', '_').replace('<', '_')
