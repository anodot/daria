import csv

from .base import Stage
from agent.pipeline.config.expression_parser import condition
from agent.pipeline import pipeline


def get_value(path, expr) -> dict:
    return {'fieldToSet': path, 'expression': '${' + expr + '}'}


def _escape_quotes(s: str) -> str:
    return s.replace("'", "\\'")


def get_convert_timestamp_to_unix_expression(timestamp_type: pipeline.TimestampType, value, timestamp_format, timezone):
    if timestamp_type == pipeline.TimestampType.STRING:
        return f"time:dateTimeToMilliseconds(time:createDateFromStringTZ({value}, '{timezone}', '{_escape_quotes(timestamp_format)}'))/1000"
    elif timestamp_type == pipeline.TimestampType.UTC_STRING:
        return f"time:dateTimeToMilliseconds(time:createDateFromStringTZ({value}, 'Etc/UTC', 'yyyy-MM-dd\\'T\\'HH:mm:ss\\'Z\\''))/1000"
    elif timestamp_type == pipeline.TimestampType.DATETIME:
        return f"(time:dateTimeToMilliseconds({value}) - time:dateTimeZoneOffset({value}, '{timezone}'))/1000"
    elif timestamp_type == pipeline.TimestampType.UNIX_MS:
        return f"{value}/1000"
    return value


def get_tags_expressions(tags: dict) -> list:
    tags_expressions = [get_value('/tags', 'emptyMap()')]
    for tag_name, tag_values in tags.items():
        tags_expressions.append(get_value(f'/tags/{tag_name}', 'emptyList()'))
        for idx, val in enumerate(tag_values):
            tags_expressions.append(get_value(f'/tags/{tag_name}[{idx}]', f'"{val}"'))
    return tags_expressions


class AddProperties(Stage):
    @classmethod
    def _get_dimension_field_path(cls, key):
        return '/properties/' + key

    def get_config(self) -> dict:
        expressions = []
        for key, val in self.pipeline.constant_dimensions.items():
            expressions.append(get_value(self._get_dimension_field_path(key), f'"{val}"'))
        timestamp_to_unix = get_convert_timestamp_to_unix_expression(self.pipeline.timestamp_type,
                                                                     "record:value('/timestamp')",
                                                                     self.pipeline.timestamp_format,
                                                                     self.pipeline.timezone)
        expressions.append(get_value('/timestamp', timestamp_to_unix))
        return {
            'expressionProcessorConfigs': get_tags_expressions(self.pipeline.get_tags()) + expressions
        }


class Filtering(Stage):
    def _get_transformations(self) -> list:
        transformations = []
        if not self.pipeline.transformations_file_path:
            return transformations

        with open(self.pipeline.transformations_file_path) as f:
            for row in csv.DictReader(f, fieldnames=['result', 'value', 'condition']):
                exp = condition.process_value(row['value'])
                if row['condition']:
                    exp = f"{condition.process_expression(row['condition'])} ? {exp} : record:value('/{row['result']}')"

                transformations.append(get_value('/' + row['result'], exp))
        return transformations

    def _check_dimensions(self) -> list:
        check_dims = []
        for d_path in self.pipeline.dimensions_paths:
            keys = d_path.split('/')
            path = '/'
            for key in keys[:-1]:
                path += key
                check_dims.append(get_value(f'{path}', f"""record:exists('{path}') && record:value('{path}') != null ? 
record:value('{path}') : emptyMap()"""))
            check_dims.append(get_value(f'/{d_path}', f"""record:exists('/{d_path}') ? 
(record:value('/{d_path}') == null) ? 'NULL' : record:value('/{d_path}') : null"""))
        return check_dims

    def get_config(self) -> dict:
        required_fields = [*self.pipeline.required_dimensions_paths, self.pipeline.timestamp_path]
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
            preconditions.append(condition.process_expression(self.pipeline.filter_condition))

        return {
            'expressionProcessorConfigs': self._check_dimensions() + self._get_transformations(),
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
                                                                     self.pipeline.timestamp_format,
                                                                     self.pipeline.timezone)
        bucket_size = self.pipeline.flush_bucket_size.total_seconds()
        watermark = f'math:floor(({timestamp_to_unix} + {bucket_size})/{bucket_size}) * {bucket_size}'
        return {
            'expressionProcessorConfigs': [get_value('/watermark', watermark),
                                           get_value('/schemaId', f'"{self.pipeline.get_schema_id()}"')]
        }


class AddMetadataTags(Stage):
    def get_config(self) -> dict:
        return {
            'expressionProcessorConfigs': get_tags_expressions(self.pipeline.meta_tags())
        }
