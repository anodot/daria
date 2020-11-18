from .base import Stage
from datetime import datetime, timedelta
from agent.pipeline import pipeline
from agent import source


class JDBCLookupStage(Stage):
    LAST_TIMESTAMP = '${record:value("/last_timestamp")}'

    def get_config(self) -> dict:
        return {
            'query': self.get_query(),
            ** self.get_connection_configs()
        }

    def get_query(self):
        timestamp_condition = f'''{self._timestamp_to_unix} > {self.LAST_TIMESTAMP} 
AND {self._timestamp_to_unix} <= {self.LAST_TIMESTAMP} + {self.pipeline.interval}'''

        query = self.pipeline.query.replace(f'{source.JDBCSource.TIMESTAMP_CONDITION}', timestamp_condition)
        return query + ' ORDER BY ' + self.pipeline.timestamp_path

    @property
    def _timestamp_to_unix(self):
        if self.pipeline.timestamp_type == pipeline.TimestampType.DATETIME:
            if self.pipeline.source.type == source.TYPE_POSTGRES:
                return f"extract(epoch from {self.pipeline.timestamp_path})"
            if self.pipeline.source.type == source.TYPE_MYSQL:
                return f"UNIX_TIMESTAMP({self.pipeline.timestamp_path})"

        if self.pipeline.timestamp_type == pipeline.TimestampType.UNIX_MS:
            return self.pipeline.timestamp_path + '/1000'

        return self.pipeline.timestamp_path

    def get_connection_configs(self):
        conf = {'hikariConfigBean.connectionString': 'jdbc:' + self.pipeline.source.config[
            source.JDBCSource.CONFIG_CONNECTION_STRING]}
        if self.pipeline.source.config[source.JDBCSource.CONFIG_USERNAME]:
            conf['hikariConfigBean.useCredentials'] = True
            conf['hikariConfigBean.username'] = self.pipeline.source.config[source.JDBCSource.CONFIG_USERNAME]
            conf['hikariConfigBean.password'] = self.pipeline.source.config[source.JDBCSource.CONFIG_PASSWORD]

        return conf
