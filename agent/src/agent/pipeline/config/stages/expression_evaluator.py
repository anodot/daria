import csv

from agent.modules.tools import escape_quotes
from .base import Stage
from agent.pipeline.config.expression_parser import condition
from agent.pipeline import pipeline, Pipeline


class AddProperties(Stage):
    @classmethod
    def _get_dimension_field_path(cls, key) -> str:
        return f'/properties/{key}'

    def get_config(self) -> dict:
        expressions = [
            get_value(self._get_dimension_field_path(key), f'"{val}"')
            for key, val in self.pipeline.static_dimensions.items()
        ]
        timestamp_to_unix = _get_convert_timestamp_to_unix_expression(
            self.pipeline.timestamp_type,
            "record:value('/timestamp')",
            self.pipeline.timestamp_format,
            self.pipeline.timezone
        )
        expressions.append(get_value('/timestamp', timestamp_to_unix))
        return {
            'expressionProcessorConfigs': _get_tags_expressions(self.pipeline) + expressions
        }


class ProcessWatermark(Stage):
    def get_config(self) -> dict:
        expressions = [get_value('/schemaId', 'SCHEMA_ID')]
        if self.pipeline.watermark_in_local_timezone:
            expressions.append(get_value('/watermark', _convert_watermark_to_timezone(self.pipeline.timezone)))
        return {
            'expressionProcessorConfigs': expressions
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
        return f'/dimensions/{key}'


def _get_convert_timestamp_to_unix_expression(
        timestamp_type: pipeline.TimestampType,
        timestamp_value: str,
        timestamp_format: str,
        timezone: str
):
    if timestamp_type == pipeline.TimestampType.STRING:
        return f"time:dateTimeToMilliseconds(time:createDateFromStringTZ({timestamp_value}, '{timezone}', '{escape_quotes(timestamp_format)}'))/1000"
    elif timestamp_type == pipeline.TimestampType.UTC_STRING:
        return f"time:dateTimeToMilliseconds(time:createDateFromStringTZ({timestamp_value}, 'Etc/UTC', 'yyyy-MM-dd\\'T\\'HH:mm:ss\\'Z\\''))/1000"
    elif timestamp_type == pipeline.TimestampType.DATETIME:
        return f"(time:dateTimeToMilliseconds({timestamp_value}) - time:dateTimeZoneOffset({timestamp_value}, '{timezone}'))/1000"
    elif timestamp_type == pipeline.TimestampType.UNIX_MS:
        return f"{timestamp_value}/1000"
    return timestamp_value


def _convert_watermark_to_timezone(timezone: str):
    return f"(record:value('/watermark') * 1000 - time:timeZoneOffset('{timezone}')) / 1000"


def _get_tags_expressions(pipeline_: Pipeline) -> list:
    tags_expressions = [get_value('/tags', 'record:value("/tags") == NULL ? emptyMap() : record:value("/tags")')]
    for tag_name, tag_values in pipeline_.get_tags().items():
        tags_expressions.append(get_value(f'/tags/{tag_name}', 'emptyList()'))
        tags_expressions.extend(get_value(f'/tags/{tag_name}[{idx}]', f'"{val}"') for idx, val in enumerate(tag_values))
    return tags_expressions


def get_value(path: str, expr: str) -> dict:
    return {'fieldToSet': path, 'expression': '${' + expr + '}'}
