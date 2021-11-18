import csv

from .base import Stage
from agent.pipeline.config.expression_parser import condition
from agent.pipeline import pipeline


def get_value(path, expr) -> dict:
    return {'fieldToSet': path, 'expression': '${' + expr + '}'}


def _escape_quotes(s: str) -> str:
    return s.replace("'", "\\'")


def get_convert_timestamp_to_unix_expression(
        timestamp_type: pipeline.TimestampType,
        timestamp_value: str,
        timestamp_format: str,
        timezone: str
):
    if timestamp_type == pipeline.TimestampType.STRING:
        return f"time:dateTimeToMilliseconds(time:createDateFromStringTZ({timestamp_value}, '{timezone}', '{_escape_quotes(timestamp_format)}'))/1000"
    elif timestamp_type == pipeline.TimestampType.UTC_STRING:
        return f"time:dateTimeToMilliseconds(time:createDateFromStringTZ({timestamp_value}, 'Etc/UTC', 'yyyy-MM-dd\\'T\\'HH:mm:ss\\'Z\\''))/1000"
    elif timestamp_type == pipeline.TimestampType.DATETIME:
        return f"(time:dateTimeToMilliseconds({timestamp_value}) - time:dateTimeZoneOffset({timestamp_value}, '{timezone}'))/1000"
    elif timestamp_type == pipeline.TimestampType.UNIX_MS:
        return f"{timestamp_value}/1000"
    return timestamp_value


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
        expressions = [
            get_value(self._get_dimension_field_path(key), f'"{val}"')
            for key, val in self.pipeline.static_dimensions.items()
        ]
        timestamp_to_unix = get_convert_timestamp_to_unix_expression(
            self.pipeline.timestamp_type,
            "record:value('/timestamp')",
            self.pipeline.timestamp_format,
            self.pipeline.timezone
        )
        expressions.append(get_value('/timestamp', timestamp_to_unix))
        return {
            'expressionProcessorConfigs': get_tags_expressions(self.pipeline.get_tags()) + expressions
        }


class Filtering(Stage):
    def _get_transformations(self) -> list:
        transformations = []
        if not self.pipeline.transformations_config:
            return transformations

        for row in csv.DictReader(self.pipeline.transformations_config.splitlines(),
                                  fieldnames=['result', 'value', 'condition']):
            exp = condition.process_value(row['value'])
            if row['condition']:
                exp = f"{condition.process_expression(row['condition'])} ? {exp} : record:value('/{row['result']}')"

            transformations.append(get_value('/' + row['result'], exp))
        return transformations

    def get_config(self) -> dict:
        preconditions = []
        if self.pipeline.filter_condition:
            preconditions.append(condition.process_expression(self.pipeline.filter_condition))

        return {
            'expressionProcessorConfigs': self._get_transformations(),
            'stageRecordPreconditions': ['${' + p + '}' for p in preconditions]
        }


class AddProperties30(AddProperties):
    @classmethod
    def _get_dimension_field_path(cls, key):
        return '/dimensions/' + key


class AddMetadataTags(Stage):
    def get_config(self) -> dict:
        return {
            'expressionProcessorConfigs': get_tags_expressions(self.pipeline.meta_tags())
        }
