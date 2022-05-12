import json

from agent.modules import tools
from agent.modules.logger import get_logger
from agent.modules.constants import HOSTNAME
from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import TestConfigHandler, NoSchemaConfigHandler, SchemaConfigHandler

logger = get_logger(__name__)


class InfluxConfigHandler(NoSchemaConfigHandler):
    stages_to_override = {
        'offset': stages.influx.InfluxScript,
        'source': stages.source.influx.InfluxSource,
        'filtering': stages.expression_evaluator.Filtering,
        'destination': stages.destination.Destination
    }

    DECLARE_VARS_JS = """
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
                        conf['value'] = [
                            '/' + d for d in tools.replace_illegal_chars(self.pipeline.required_dimensions)
                        ]

                    if conf['name'] == 'initScript':
                        conf['value'] = self._get_js_vars()

    def _get_js_vars(self) -> str:
        return self.DECLARE_VARS_JS.format(
            required_dimensions=str(self.pipeline.required_dimensions),
            optional_dimensions=str(self.pipeline.optional_dimensions),
            measurement_name=tools.replace_illegal_chars(self.pipeline.config.get('measurement_name', {})),
            target_type=self.pipeline.config.get('target_type', 'gauge'),
            constant_properties=str(self.pipeline.static_dimensions),
            host_id=self.pipeline.destination.host_id,
            host_name=HOSTNAME,
            pipeline_id=self.pipeline.name,
            tags=json.dumps(self.pipeline.get_tags())
        )


class InfluxSchemaConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'offset': stages.influx.InfluxScript,
        'source': stages.source.influx.InfluxSource,
        'transform_records': stages.js_convert_metrics.JSConvertMetrics30,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties30,
        'filtering': stages.expression_evaluator.Filtering,
        'destination': stages.destination.Destination,
        'destination_watermark': stages.destination.WatermarkDestination,
    }


class Influx2SchemaConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.influx2.Influx2Source,
        'jython_transform_records': stages.influx.JythonTransformRecords,
        'js_create_metrics': stages.js_convert_metrics.JSConvertMetrics30,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties30,
        'filtering': stages.expression_evaluator.Filtering,
        'destination': stages.destination.Destination,
        'destination_watermark': stages.destination.WatermarkDestination,
    }


class TestInfluxConfigHandler(TestConfigHandler):
    stages_to_override = {
        'source': stages.source.influx.TestInfluxSource,
    }


class TestInflux2ConfigHandler(TestConfigHandler):
    stages_to_override = {
        'source': stages.source.influx2.TestInflux2Source,
    }
