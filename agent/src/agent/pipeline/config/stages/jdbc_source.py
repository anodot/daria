from .base import Stage
from datetime import datetime, timedelta
from agent.pipeline import pipeline
from agent import source


class JDBCSourceStage(Stage):
    def get_config(self) -> dict:
        return {
            'query': self.get_query(),
            'queryInterval': '${' + str(self.pipeline.interval) + ' * SECONDS}',
            'offsetColumn': self.pipeline.timestamp_path,
            'initialOffset': self.get_initial_offset(),
            **self.get_connection_configs()
        }

    def get_query(self):
        timestamp_condition = self.get_timestamp_condition() + f' AND {self.pipeline.timestamp_path} <= {self.get_interval()}'
        if self.pipeline.delay:
            timestamp_condition += f' AND {self.pipeline.timestamp_path} < {self.get_delay()}'
        return self.pipeline.query.replace(f'{source.JDBCSource.TIMESTAMP_CONDITION}',
                                           timestamp_condition) + ' ORDER BY ' + self.pipeline.timestamp_path

    def get_timestamp_condition(self):
        if self.pipeline.timestamp_type == pipeline.TimestampType.DATETIME:
            if self.pipeline.source.type == source.TYPE_POSTGRES:
                return f"{self.pipeline.timestamp_path} > timestamp '${{OFFSET}}'"
            return f'{self.pipeline.timestamp_path} > "${{OFFSET}}"'

        return f'{self.pipeline.timestamp_path} > ${{OFFSET}}'

    def get_interval(self):
        if self.pipeline.timestamp_type == pipeline.TimestampType.DATETIME:
            if self.pipeline.source.type == source.TYPE_MYSQL:
                return f'DATE_ADD("${{OFFSET}}", INTERVAL {self.pipeline.interval} SECOND)'
            if self.pipeline.source.type == source.TYPE_POSTGRES:
                return f"timestamp '${{OFFSET}}' + INTERVAL '{self.pipeline.interval} SECOND'"
        elif self.pipeline.timestamp_type == pipeline.TimestampType.UNIX_MS:
            return '${OFFSET} + ' + str(self.pipeline.interval * 1e3)
        return '${OFFSET} + ' + str(self.pipeline.interval)

    def get_delay(self):
        if self.pipeline.timestamp_type == pipeline.TimestampType.DATETIME:
            return f"NOW() - INTERVAL '{self.pipeline.delay}' MINUTE"
        if self.pipeline.source.type == source.TYPE_POSTGRES:
            curr_timestamp = 'extract(epoch from now())'
        else:
            curr_timestamp = 'UNIX_TIMESTAMP()'
        unix_t = f'({curr_timestamp} - {self.pipeline.delay}*60)'
        if self.pipeline.timestamp_type == pipeline.TimestampType.UNIX_MS:
            unix_t += '*1000'
        return unix_t

    def get_initial_offset(self):
        timestamp = (datetime.now() - timedelta(days=int(self.pipeline.days_to_backfill)) - timedelta(
            seconds=self.pipeline.interval)).replace(second=0)
        if self.pipeline.timestamp_type == pipeline.TimestampType.DATETIME:
            return timestamp.strftime('%Y-%m-%d %H:%M:%S')
        elif self.pipeline.timestamp_type == pipeline.TimestampType.UNIX_MS:
            return str(int(timestamp.timestamp() * 1e3))

        return str(int(timestamp.timestamp()))

    def get_connection_configs(self):
        conf = {'hikariConfigBean.connectionString': 'jdbc:' + self.pipeline.source.config[
            source.JDBCSource.CONFIG_CONNECTION_STRING]}
        if self.pipeline.source.config[source.JDBCSource.CONFIG_USERNAME]:
            conf['hikariConfigBean.useCredentials'] = True
            conf['hikariConfigBean.username'] = self.pipeline.source.config[source.JDBCSource.CONFIG_USERNAME]
            conf['hikariConfigBean.password'] = self.pipeline.source.config[source.JDBCSource.CONFIG_PASSWORD]

        return conf
