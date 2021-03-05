from agent.pipeline.config import stages
from agent.pipeline.config.handlers.schema import SchemaConfigHandler


class DirectoryConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.source.Source,
        'JavaScriptEvaluator_01': stages.js_convert_metrics.JSConvertMetrics30,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties30,
        'ExpressionEvaluator_03': stages.expression_evaluator.Filtering,
        'process_finish_file_event': stages.expression_evaluator.SendWatermark,
        'destination': stages.destination.Destination,
        'destination_watermark': stages.destination.WatermarkDestination,
    }
