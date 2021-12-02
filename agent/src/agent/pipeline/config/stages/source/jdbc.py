from agent.pipeline.config.stages.base import Stage
from agent import pipeline, source


class JDBCSource(Stage):
    def get_config(self) -> dict:
        return {
            'query': pipeline.jdbc.query.Builder(self.pipeline).build(),
            'hikariConfigBean.connectionString': self._get_connection_string(),
            source.JDBCSource.CONFIG_USE_CREDENTIALS: self._config_contains_username(),
            **{key: val for key, val in self.pipeline.source.config.items() if key.startswith('hikariConfigBean')}
        }

    def _config_contains_username(self) -> bool:
        return bool(self.pipeline.source.config.get(source.JDBCSource.CONFIG_USERNAME))

    def _get_connection_string(self) -> str:
        return 'jdbc:' + self.pipeline.source.config[source.JDBCSource.CONFIG_CONNECTION_STRING]
