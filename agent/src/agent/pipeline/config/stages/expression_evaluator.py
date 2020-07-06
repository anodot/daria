import csv

from .base import Stage
from agent.pipeline.pipeline import TimestampType
from agent.pipeline.config.expression_parser import condition


def get_value(path, expr) -> dict:
    return {'fieldToSet': path, 'expression': '${' + expr + '}'}


def get_convert_timestamp_to_unix_expression(timestamp_type: TimestampType, value, timestamp_format):
    if timestamp_type == TimestampType.STRING:
        return f"time:dateTimeToMilliseconds(time:extractDateFromString({value}, '{timestamp_format}'))/1000"
    elif timestamp_type == TimestampType.UTC_STRING:
        return f"time:dateTimeToMilliseconds(time:createDateFromStringTZ({value}, 'Etc/UTC', 'yyyy-MM-dd\\'T\\'HH:mm:ss.SSS\\'Z\\''))/1000"
    elif timestamp_type == TimestampType.DATETIME:
        return f"time:dateTimeToMilliseconds({value})/1000"
    elif timestamp_type == TimestampType.UNIX_MS:
        return f"{value}/1000"
    return value


class AddProperties(Stage):

    @classmethod
    def _get_dimension_field_path(cls, key):
        return '/properties/' + key

    def get_tags(self) -> list:
        tags_expressions = [get_value('/tags', 'emptyMap()')]
        for tag_name, tag_values in self.pipeline.get_tags().items():
            tags_expressions.append(get_value(f'/tags/{tag_name}', 'emptyList()'))
            for idx, val in enumerate(tag_values):
                tags_expressions.append(get_value(f'/tags/{tag_name}[{idx}]', f'"{val}"'))
        return tags_expressions

    def get_config(self) -> dict:
        expressions = []
        for key, val in self.pipeline.constant_dimensions.items():
            expressions.append(get_value(self._get_dimension_field_path(key), f'"{val}"'))
        timestamp_to_unix = get_convert_timestamp_to_unix_expression(self.pipeline.timestamp_type,
                                                                     "record:value('/timestamp')",
                                                                     self.pipeline.timestamp_format)
        expressions.append(get_value('/timestamp', timestamp_to_unix))
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
        required_fields = [*self.pipeline.required_dimensions_paths,
                           self.pipeline.timestamp_path]
        if self.pipeline.values_array_path:
            required_fields.append(self.pipeline.values_array_path)
        else:
            required_fields += self.pipeline.values_paths

        if not self.pipeline.static_what:
            required_fields += self.pipeline.measurement_names_paths
            for t_type in self.pipeline.target_types_paths:
                if t_type not in self.pipeline.TARGET_TYPES:
                    required_fields.append(t_type)

        preconditions = []
        if self.pipeline.filter_condition:
            preconditions.append(condition.get_expression(self.pipeline.filter_condition))

        return {
            'expressionProcessorConfigs': self.check_dimensions() + self.get_transformations(),
            'stageRequiredFields': [f'/{f}' for f in required_fields],
            'stageRecordPreconditions': ['${' + p + '}' for p in preconditions]
        }


class AddProperties30(AddProperties):
    @classmethod
    def _get_dimension_field_path(cls, key):
        return '/dimensions/' + key


class SendWatermark(Stage):
    def get_config(self) -> dict:
        extract_timestamp = "str:regExCapture(record:value('/filepath'), '.*/(.+)_.*', 1)"
        timestamp_to_unix = get_convert_timestamp_to_unix_expression(self.pipeline.timestamp_type,
                                                                     extract_timestamp,
                                                                     self.pipeline.timestamp_format)
        bucket_size = self.pipeline.flush_bucket_size.total_seconds()
        watermark = f'math:floor(({timestamp_to_unix} + {bucket_size})/{bucket_size}) * {bucket_size}'
        return {
            'expressionProcessorConfigs': [get_value('/watermark', watermark),
                                           get_value('/schemaId', f'"{self.pipeline.get_schema_id()}"')]
        }
