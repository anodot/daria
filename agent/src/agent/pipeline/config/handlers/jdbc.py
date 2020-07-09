from .base import BaseConfigHandler, ConfigHandlerException
from agent.logger import get_logger
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import urlparse, urlunparse
from agent.pipeline.config import stages
from agent.pipeline import pipeline

logger = get_logger(__name__)


class JDBCConfigHandler(BaseConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'jdbc_http.json'
    PIPELINES_BASE_CONFIGS_PATH = 'base_pipelines/jdbc_{destination_name}.json'

    QUERY = "SELECT * FROM {table} WHERE {offset_column} > ${{OFFSET}} {condition} ORDER BY {offset_column} LIMIT {limit}"

    stages = {
        'source': stages.source.Source,
        'JavaScriptEvaluator_01': stages.js_convert_metrics_20.JSConvertMetrics,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination
    }

    def override_stages(self):
        self.update_source_configs()
        super().override_stages()

    def update_source_configs(self):
        source_config = self.pipeline.source.config

        condition = self.pipeline.config.get('condition')
        condition = f'AND ({condition})' if condition else ''

        offset_column = self.pipeline.config.get('offset_column', self.pipeline.timestamp_path)

        limit = self.pipeline.config.get('limit', 1000)
        source_config['query'] = self.QUERY.format(**{
            'table': self.pipeline.config['table'],
            'offset_column': offset_column,
            'condition': condition,
            'limit': limit
        })
        source_config['hikariConfigBean.connectionString'] = 'jdbc:' + source_config['connection_string']
        source_config['queryInterval'] = '${' + str(source_config.get('query_interval', '10')) + ' * SECONDS}'
        source_config['commonSourceConfigBean.maxBatchSize'] = limit
        source_config['offsetColumn'] = offset_column
        self.set_initial_offset()

    def set_initial_offset(self):
        source_config = self.pipeline.source.config

        timestamp = datetime.now() - timedelta(days=int(self.pipeline.config.get('initial_offset', 3)))
        start = str(int(timestamp.timestamp()))
        if self.pipeline.timestamp_type == pipeline.TimestampType.DATETIME:
            start = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        elif self.pipeline.timestamp_type == pipeline.TimestampType.DATETIME:
            start = str(int(timestamp.timestamp() * 1e3))

        if self.pipeline.config['offset_column'] == self.pipeline.timestamp_path:
            source_config['initialOffset'] = start
            return

        self.get_initial_offset_value_from_db(start)

    def get_initial_offset_value_from_db(self, start):
        source_config = self.pipeline.source.config
        conn_info = urlparse(source_config['connection_string'])
        if source_config.get('hikariConfigBean.useCredentials'):
            userpass = source_config['hikariConfigBean.username'] + ':' + source_config['hikariConfigBean.password']
            netloc = userpass + '@' + conn_info.netloc
        else:
            netloc = conn_info.netloc

        scheme = conn_info.scheme + '+mysqlconnector' if self.pipeline.source.type == 'mysql' else conn_info.scheme
        try:
            eng = create_engine(urlunparse((scheme, netloc, conn_info.path, '', '', '')))
            with eng.connect() as con:
                result = con.execute("""SELECT {offset}, {timestamp} FROM {table} 
                                    WHERE {timestamp} <= '{start}' ORDER BY {offset} DESC LIMIT 1""".format(
                                        table=self.pipeline.config['table'],
                                        offset=self.pipeline.config['offset_column'],
                                        timestamp=self.pipeline.timestamp_path,
                                        start=start
                                    ))

                res = result.fetchone()
                source_config['initialOffset'] = str(res[0]) if res else '0'
        except SQLAlchemyError as e:
            raise ConfigHandlerException(str(e))
