from agent import pipeline, source
from agent.pipeline import Pipeline

TIMESTAMP_CONDITION = '{TIMESTAMP_CONDITION}'
TIMESTAMP_COLUMN = '{TIMESTAMP_COLUMN}'
LAST_TIMESTAMP_VALUE = '{LAST_TIMESTAMP_VALUE}'
INTERVAL = '{INTERVAL}'
LAST_TIMESTAMP = '${record:value("/last_timestamp")}'
LAST_TIMESTAMP_ISO = '${record:value("/last_timestamp_iso")}'
LAST_TIMESTAMP_TEMPLATE = '%last_timestamp%'


class Builder:
    TIMESTAMP_VALUE = LAST_TIMESTAMP
    TIMESTAMP_VALUE_ISO = LAST_TIMESTAMP_ISO

    def __init__(self, pipeline_: Pipeline):
        self.pipeline = pipeline_

    def build(self):
        if isinstance(self.pipeline, pipeline.TestPipeline):
            return self._get_preview_query()

        query = self.pipeline.query
        if TIMESTAMP_CONDITION in self.pipeline.query:
            query = f'{query} ORDER BY {self.pipeline.timestamp_path}'
            replacements = {
                f'{TIMESTAMP_CONDITION}': self._get_timestamp_condition(),
            }
        else:
            replacements = {
                f'{TIMESTAMP_COLUMN}': self.pipeline.timestamp_path,
                f'{LAST_TIMESTAMP_VALUE}': self.TIMESTAMP_VALUE,
                f'{INTERVAL}': str(self.pipeline.interval),
            }
        return [query := query.replace(k, v) for k, v in replacements.items()][-1]

    def _get_preview_query(self):
        if not self.pipeline.query:
            # dummy query for validating source connection in streamsets
            return 'SELECT * FROM t'
        query = self.pipeline.query.replace(TIMESTAMP_CONDITION, '1=1')
        return f'{query} LIMIT {pipeline.manager.MAX_SAMPLE_RECORDS}'

    def _get_timestamp_condition(self) -> str:
        if self._supports_indexed_timestamp_condition():
            return self._get_indexed_query()
        return self._get_regular_query()

    def _supports_indexed_timestamp_condition(self) -> bool:
        return self.pipeline.timestamp_type in [pipeline.TimestampType.DATETIME, pipeline.TimestampType.STRING] and \
               self.pipeline.source.type in [source.TYPE_MSSQL, source.TYPE_IMPALA, source.TYPE_DRUID]

    def _get_indexed_query(self) -> str:
        if self.pipeline.source.type == source.TYPE_DRUID:
            return f'TIME_IN_INTERVAL("{self.pipeline.timestamp_path}", ' \
                   f'\'{self.TIMESTAMP_VALUE_ISO}/PT{self.pipeline.interval}S\')'
        if self.pipeline.source.type == source.TYPE_MSSQL:
            return f"{self.pipeline.timestamp_path} BETWEEN DATEADD(second, {self.TIMESTAMP_VALUE}, '1970-01-01') AND "\
                   f"DATEADD(second, {self.TIMESTAMP_VALUE} + {self.pipeline.interval}, '1970-01-01')"
        if self.pipeline.source.type == source.TYPE_IMPALA:
            return f"{self.pipeline.timestamp_path} BETWEEN CAST(FROM_UNIXTIME({self.TIMESTAMP_VALUE}) as TIMESTAMP) AND " \
                   f"CAST(FROM_UNIXTIME({self.TIMESTAMP_VALUE}) as TIMESTAMP) + interval {self.pipeline.interval} seconds"

    def _get_regular_query(self) -> str:
        return f'{self._timestamp_to_unix()} >= {self.TIMESTAMP_VALUE} AND ' \
               f'{self._timestamp_to_unix()} < {self.TIMESTAMP_VALUE} + {self.pipeline.interval}'

    def _timestamp_to_unix(self):
        if self.pipeline.timestamp_type == pipeline.TimestampType.DATETIME:
            if self.pipeline.source.type == source.TYPE_POSTGRES:
                return f"extract(epoch from {self.pipeline.timestamp_path})"
            if self.pipeline.source.type == source.TYPE_MYSQL:
                return f"UNIX_TIMESTAMP({self.pipeline.timestamp_path})"
            if self.pipeline.source.type == source.TYPE_CLICKHOUSE:
                return f"toUnixTimestamp({self.pipeline.timestamp_path})"
            if self.pipeline.source.type == source.TYPE_ORACLE:
                return f"""(cast(sys_extract_utc(from_tz(cast({self.pipeline.timestamp_path} as TIMESTAMP), 
'{self.pipeline.timezone}')) as date) - TO_DATE('1970-01-01 00:00:00','YYYY-MM-DD HH24:MI:SS')) * 86400"""
            if self.pipeline.source.type == source.TYPE_DATABRICKS:
                return f"unix_timestamp({self.pipeline.timestamp_path})"
            if self.pipeline.source.type == source.TYPE_IMPALA:
                return f"UNIX_TIMESTAMP({self.pipeline.timestamp_path})"

        if self.pipeline.timestamp_type == pipeline.TimestampType.UNIX_MS:
            return f'{self.pipeline.timestamp_path}/1000'

        return self.pipeline.timestamp_path


class TemplateBuilder(Builder):
    TIMESTAMP_VALUE = LAST_TIMESTAMP_TEMPLATE


class SolarWindsBuilder(Builder):
    def _get_timestamp_condition(self) -> str:
        date_time = f"DateTime('{LAST_TIMESTAMP_TEMPLATE}')"
        return f'{self.pipeline.timestamp_path} > {date_time}' \
               f' AND {self.pipeline.timestamp_path} <= AddSecond({self.pipeline.interval}, {date_time})'
