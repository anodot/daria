from agent.pipeline.config.stages.base import Stage
from agent import pipeline, source


class JDBCSource(Stage):
    LAST_TIMESTAMP = '${record:value("/last_timestamp")}'

    def _get_config(self) -> dict:
        return {
            'query': self.get_query(),
            ** self.get_connection_configs()
        }

    def get_query(self):
        if isinstance(self.pipeline, pipeline.TestPipeline):
            return self._get_preview_query()

        timestamp_condition = f'''{self._timestamp_to_unix} > {self.LAST_TIMESTAMP} 
AND {self._timestamp_to_unix} <= {self.LAST_TIMESTAMP} + {self.pipeline.interval}'''

        query = self.pipeline.query.replace(f'{source.JDBCSource.TIMESTAMP_CONDITION}', timestamp_condition)
        return query + ' ORDER BY ' + self.pipeline.timestamp_path

    def _get_preview_query(self):
        if not self.pipeline.query:
            # dummy query for validating source connection in streamsets
            return 'SELECT * FROM t'
        query = self.pipeline.query.replace(f'{source.JDBCSource.TIMESTAMP_CONDITION}', 'true')
        return query + f' LIMIT {pipeline.manager.MAX_SAMPLE_RECORDS}'

    @property
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

    def get_connection_configs(self):
        conf = {'hikariConfigBean.connectionString': 'jdbc:' + self.pipeline.source.config[
            source.JDBCSource.CONFIG_CONNECTION_STRING]}
        if self.pipeline.source.config.get(source.JDBCSource.CONFIG_USERNAME):
            conf['hikariConfigBean.useCredentials'] = True
            conf['hikariConfigBean.username'] = self.pipeline.source.config[source.JDBCSource.CONFIG_USERNAME]
            conf['hikariConfigBean.password'] = self.pipeline.source.config[source.JDBCSource.CONFIG_PASSWORD]

        return conf
