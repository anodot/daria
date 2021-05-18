import json

from . import base
from agent.modules.logger import get_logger
from agent.modules.constants import HOSTNAME
from agent.pipeline.config import stages
from .schema import SchemaConfigHandler

logger = get_logger(__name__)

class InfluxConfigHandler(base.BaseConfigHandler):
    stages_to_override = {
        'offset': stages.influx_offset.InfluxScript,
        'source': stages.source.influx.InfluxSource,
        'destination': stages.destination.Destination
    }

    DECLARE_VARS_JS = """
state['MEASUREMENT_NAME'] = '{measurement_name}';
state['MEASUREMENT_NAMES'] = {measurement_names};
state['REQUIRED_DIMENSIONS'] = {required_dimensions};
state['OPTIONAL_DIMENSIONS'] = {optional_dimensions};
state['TARGET_TYPE'] = '{target_type}';
state['TARGET_TYPES'] = {target_types};
state['CONSTANT_PROPERTIES'] = {constant_properties}
state['HOST_ID'] = '{host_id}'
state['HOST_NAME'] = '{host_name}'
state['PIPELINE_ID'] = '{pipeline_id}'
state['TAGS'] = {tags}
state['INTERVAL'] = {interval}
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
                            measurement_names=list(self.pipeline.config.get('values', {}).keys()),
                            target_types=list(self.pipeline.config.get('values', {}).values()),
                            target_type=self.pipeline.config.get('target_type', 'gauge'),
                            constant_properties=str(self.pipeline.static_dimensions),
                            host_id=self.pipeline.destination.host_id,
                            host_name=HOSTNAME,
                            pipeline_id=self.pipeline.name,
                            tags=json.dumps(self.pipeline.get_tags()),
                            interval=int(self.pipeline.config['interval'])
                        )

    def get_required_dimensions(self):
        return [self.replace_illegal_chars(d) for d in self.pipeline.config['dimensions']['required']]

    def get_optional_dimensions(self):
        return [self.replace_illegal_chars(d) for d in self.pipeline.config['dimensions'].get('optional', [])]

    @staticmethod
    def replace_illegal_chars(string: str) -> str:
        return string.replace(' ', '_').replace('.', '_').replace('<', '_')


class InfluxSchemaConfigHandler(SchemaConfigHandler, InfluxConfigHandler):
    stages_to_override = {
        'offset': stages.influx_offset.InfluxScript,
        'source': stages.source.influx.InfluxSource,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties30,
        'destination': stages.destination.Destination
    }
