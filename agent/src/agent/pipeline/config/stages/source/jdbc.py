from agent.pipeline.config.stages.base import Stage
from agent import pipeline, source


class JDBCSource(Stage):
    def get_config(self) -> dict:
        return {
            'query': pipeline.jdbc.query.Builder(self.pipeline).build(),
            ** self.get_connection_configs()
        }

    def get_connection_configs(self):
        conf = {'hikariConfigBean.connectionString': 'jdbc:' + self.pipeline.source.config[
            source.JDBCSource.CONFIG_CONNECTION_STRING]}
        if self.pipeline.source.config.get(source.JDBCSource.CONFIG_USERNAME):
            conf['hikariConfigBean.useCredentials'] = True
            conf['hikariConfigBean.username'] = self.pipeline.source.config[source.JDBCSource.CONFIG_USERNAME]
            conf['hikariConfigBean.password'] = self.pipeline.source.config[source.JDBCSource.CONFIG_PASSWORD]

        return conf
