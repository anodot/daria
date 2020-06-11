import csv

from .base import Stage
from agent.constants import HOSTNAME
from agent.pipeline.pipeline import TimestampType
from agent.pipeline.config.expression_parser import condition


def get_value(path, expr) -> dict:
    return {'fieldToSet': path, 'expression': '${' + expr + '}'}


class AddProperties(Stage):
    def get_default_tags(self) -> dict:
        return {
            'source': ['anodot-agent'],
            'source_host_id': [self.pipeline.destination.host_id],
            'source_host_name': [HOSTNAME],
            'pipeline_id': [self.pipeline.id],
            'pipeline_type': [self.pipeline.source.type]
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

    def get_tags(self) -> list:
        tags = {
            **self.get_default_tags(),
            **self.pipeline.tags
        }
        tags_expressions = [get_value('/tags', 'emptyMap()')]
        for tag_name, tag_values in tags.items():
            tags_expressions.append(get_value(f'/tags/{tag_name}', 'emptyList()'))
            for idx, val in enumerate(tag_values):
                tags_expressions.append(get_value(f'/tags/{tag_name}[{idx}]', f'"{val}"'))
        return tags_expressions

    def get_config(self) -> dict:
        expressions = []
        for key, val in self.pipeline.constant_dimensions.items():
            expressions.append(get_value(self._get_dimension_field_path(key), f'"{val}"'))
        expressions.append(get_value('/timestamp',
                                     self.get_convert_timestamp_to_unix_expression("record:value('/timestamp')")))
        return {
            'expressionProcessorConfigs': self.get_tags() + expressions
        }


class Filtering(Stage):
    def get_transformations(self):
        transformations = []
        if not self.pipeline.transformations_file_path:
            return transformations

        with open(self.pipeline.transformations_file_path) as f:
            for row in csv.DictReader(f, fieldnames=['result', 'value', 'condition']):
                exp = f"'{row['value']}'"
                if row['condition']:
                    exp = f"{condition.get_expression(row['condition'])} ? {exp} : record:value('/{row['result']}')"

                transformations.append(get_value('/' + row['result'], exp))
        return transformations

    def check_dimensions(self):
        check_dims = []
        for d_path in self.pipeline.dimensions_paths:
            check_dims.append(get_value(f'/{d_path}', f"""record:exists('/{d_path}') ? 
(record:value('/{d_path}') == null) ? 'NULL' : record:value('/{d_path}') : null"""))
        return check_dims

    def get_config(self) -> dict:

        # TODO: add conditions for non-static what
        required_fields = [*self.pipeline.values_paths, *self.pipeline.required_dimensions_paths,
                           self.pipeline.timestamp_path]

        preconditions = []
        if self.pipeline.filter_condition:
            preconditions.append(condition.get_expression(self.pipeline.filter_condition))

        return {
            'expressionProcessorConfigs': self.check_dimensions() + self.get_transformations(),
            'stageRequiredFields': [f'/{f}' for f in required_fields],
            'stageRecordPreconditions': ['${' + p + '}' for p in preconditions]
        }
