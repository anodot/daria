import csv

from .base import Stage
from agent.constants import HOSTNAME
from agent.pipeline.pipeline import TimestampType
from agent.pipeline.config.expression_parser import condition


class AddProperties(Stage):
    def get_default_tags(self) -> dict:
        return {
            'source': ['anodot-agent'],
            'source_host_id': [self.pipeline.destination.host_id],
            'source_host_name': [HOSTNAME],
            'pipeline_id': [self.pipeline.id],
            'pipeline_type': [self.pipeline.source.type]
        }

    def get_tags(self) -> dict:
        return {
            **self.get_default_tags(),
            **self.pipeline.tags
        }

    @classmethod
    def _get_dimension_field_path(cls, key):
        return '/properties/' + key

    def get_convert_timestamp_to_unix_expression(self, value):
        if self.pipeline.timestamp_type == TimestampType.STRING:
            dt_format = self.pipeline.timestamp_format
            return f"time:dateTimeToMilliseconds(time:extractDateFromString({value}, '{dt_format}'))/1000"
        elif self.pipeline.timestamp_type == TimestampType.DATETIME:
            return f"time:dateTimeToMilliseconds({value})/1000"
        elif self.pipeline.timestamp_type == TimestampType.UNIX_MS:
            return f"{value}/1000"
        return value

    def get_expressions(self) -> dict:
        tags = {'/tags': '${emptyMap()}'}
        for tag_name, tag_values in self.get_tags().items():
            tags[f'/tags/{tag_name}'] = '${emptyList()}'
            for idx, val in enumerate(tag_values):
                tags[f'/tags/{tag_name}[{idx}]']: val
        return {
            **tags,
            **{self._get_dimension_field_path(key): val for key, val in self.pipeline.constant_dimensions.items()},
            '/timestamp': self.get_convert_timestamp_to_unix_expression("record:value('/timestamp')")
        }

    def get_config(self) -> dict:
        expressions = [{'fieldToSet': path, 'expression': '${' + expr + '}'} for path, expr in self.get_expressions()]
        return {
            'expressionProcessorConfigs': expressions
        }


class Filtering(Stage):
    def get_transformations(self):
        transformations = {}
        if not self.pipeline.transformations_file_path:
            return transformations

        with open(self.pipeline.transformations_file_path) as f:
            for row in csv.DictReader(f, fieldnames=['result', 'value', 'condition']):
                exp = f"'{row['value']}'"
                if row['condition']:
                    exp = f"{condition.get_expression(row['condition'])} ? {exp} : record:value('/{row['result']}')"

                transformations['/' + row['result']] = exp
        return transformations

    def check_dimensions(self):
        check_dims = {}
        for d_path in self.pipeline.dimensions_paths:
            check_dims[f'/{d_path}'] = f"""record:exists('/{d_path}') ? 
(record:value('/{d_path}') == null) ? 'NULL' : record:value('/{d_path}') : null"""
        return check_dims

    def get_expressions(self) -> dict:
        return {
            **self.get_transformations(),
            **self.check_dimensions()
        }

    def get_config(self) -> dict:
        expressions = [{'fieldToSet': path, 'expression': '${' + expr + '}'} for path, expr in self.get_expressions()]

        # TODO: add conditions for non-static what
        required_fields = [*self.pipeline.values_paths, *self.pipeline.required_dimensions_paths,
                           self.pipeline.timestamp_path]

        return {
            'expressionProcessorConfigs': expressions,
            'stageRequiredFields': [f'/{f}' for f in required_fields],
            'stageRecordPreconditions': [condition.get_expression(self.pipeline.filter_condition)]
        }
