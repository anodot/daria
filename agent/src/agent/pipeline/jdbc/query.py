from agent import pipeline, source
from agent.pipeline import Pipeline

TIMESTAMP_CONDITION = '{TIMESTAMP_CONDITION}'
LAST_TIMESTAMP = '${record:value("/last_timestamp")}'
LAST_TIMESTAMP_TEMPLATE = '{LAST_TIMESTAMP}'


class Builder:
    TIMESTAMP_VALUE = LAST_TIMESTAMP

    def __init__(self, pipeline_: Pipeline):
        self.pipeline = pipeline_
    
    def build(self):
        if isinstance(self.pipeline, pipeline.TestPipeline):
            return self._get_preview_query()
        query = self.pipeline.query.replace(f'{TIMESTAMP_CONDITION}', self._get_timestamp_condition())
        return query + ' ORDER BY ' + self.pipeline.timestamp_path
    
    def _get_preview_query(self):
        if not self.pipeline.query:
            # dummy query for validating source connection in streamsets
            return 'SELECT * FROM t'
        query = self.pipeline.query.replace(f'{TIMESTAMP_CONDITION}', 'true')
        return query + f' LIMIT {pipeline.manager.MAX_SAMPLE_RECORDS}'
    
    def _get_timestamp_condition(self) -> str:
        return f'{self._timestamp_to_unix()} > {self.TIMESTAMP_VALUE}' \
               f' AND {self._timestamp_to_unix()} <= {self.TIMESTAMP_VALUE} + {self.pipeline.interval}'
    
    def _timestamp_to_unix(self):
        if self.pipeline.timestamp_type == pipeline.TimestampType.DATETIME:
            if self.pipeline.source.type == source.TYPE_POSTGRES:
                return f"extract(epoch from {self.pipeline.timestamp_path})"
            if self.pipeline.source.type == source.TYPE_MYSQL:
                return f"UNIX_TIMESTAMP({self.pipeline.timestamp_path})"
            if self.pipeline.source.type == source.TYPE_CLICKHOUSE:
                return f"toUnixTimestamp({self.pipeline.timestamp_path})"
    
        if self.pipeline.timestamp_type == pipeline.TimestampType.UNIX_MS:
            return self.pipeline.timestamp_path + '/1000'
    
        return self.pipeline.timestamp_path


class TemplateBuilder(Builder):
    TIMESTAMP_VALUE = LAST_TIMESTAMP_TEMPLATE