from agent.pipeline.config.stages.base import Stage
from agent import pipeline, source


class JDBCSource(Stage):
    def get_config(self) -> dict:
        return {
            'query': pipeline.jdbc.query.Builder(self.pipeline).build(),
            **self.get_connection_configs()
        }

    def get_connection_configs(self):
        conn_str = 'jdbc:' + self.pipeline.source.config[source.JDBCSource.CONFIG_CONNECTION_STRING]
        conf = {
            'hikariConfigBean.connectionString': conn_str,
            **{key: val for key, val in self.pipeline.source.config.items() if key.startswith('hikariConfigBean')}
        }
        if self.pipeline.source.config.get(source.JDBCSource.CONFIG_USERNAME):
            conf['hikariConfigBean.useCredentials'] = True

        return conf
