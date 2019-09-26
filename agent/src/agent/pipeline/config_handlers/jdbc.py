from .base import BaseConfigHandler, ConfigHandlerException
from agent.logger import get_logger
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import urlparse, urlunparse

logger = get_logger(__name__)


class JDBCConfigHandler(BaseConfigHandler):
    DECLARE_VARS_JS = """/*
state['TABLE_NAME'] = 'test';
state['TIMESTAMP_COLUMN'] = 'timestamp_unix';
state['DIMENSIONS'] = ['ver', 'AdSize', 'Country', 'AdType', 'Exchange'];
state['VALUES_COLUMNS'] = ['Clicks', 'Impressions'];
state['TARGET_TYPES'] = ['gauge', 'counter']
state['COUNT_RECORDS'] = 1
*/

state['TABLE_NAME'] = '{table_name}';
state['TIMESTAMP_COLUMN'] = '{timestamp_column}';
state['DIMENSIONS'] = {dimensions};
state['VALUES_COLUMNS'] = {values};
state['TARGET_TYPES'] = {target_types}
state['COUNT_RECORDS'] = {count_records}
"""
    PIPELINES_BASE_CONFIGS_PATH = 'base_pipelines/jdbc_{destination_name}.json'

    QUERY = "SELECT * FROM {table} WHERE {offset_column} > ${{OFFSET}} {condition} ORDER BY {offset_column} LIMIT {limit}"

    def override_stages(self):

        self.update_source_configs()

        for stage in self.config['stages']:

            if stage['instanceName'] == 'JavaScriptEvaluator_01':
                for conf in stage['configuration']:
                    if conf['name'] == 'stageRequiredFields':
                        conf['value'] = ['/' + d for d in self.client_config['dimensions']]
                        conf['value'].append('/' + self.client_config['timestamp']['name'])

                    if conf['name'] == 'initScript':
                        conf['value'] = self.DECLARE_VARS_JS.format(
                            table_name=str(self.client_config['table']),
                            timestamp_column=str(self.client_config['timestamp']['name']),
                            dimensions=self.client_config['dimensions'],
                            values=str(list(self.client_config['values'].keys())),
                            target_types=str(list(self.client_config['values'].values())),
                            count_records=int(self.client_config.get('count_records', False))
                        )

            if stage['instanceName'] == 'ExpressionEvaluator_02':
                self.set_constant_properties(stage)
                self.convert_timestamp_to_unix(stage)

        self.update_destination_config()

    def update_source_configs(self):

        source_config = self.client_config['source']['config']

        condition = self.client_config.get('condition')
        condition = f'AND ({condition})' if condition else ''

        offset_column = self.client_config.get('offset_column', self.client_config['timestamp']['name'])

        limit = self.client_config.get('limit', 1000)
        source_config['query'] = self.QUERY.format(**{
            'table': self.client_config['table'],
            'offset_column': offset_column,
            'condition': condition,
            'limit': limit
        })
        source_config['hikariConfigBean.connectionString'] = 'jdbc:' + source_config['connection_string']
        source_config['queryInterval'] = '${' + str(source_config.get('query_interval', '10')) + ' * SECONDS}'
        source_config['commonSourceConfigBean.maxBatchSize'] = limit
        source_config['offsetColumn'] = offset_column
        self.set_initial_offset()

        super().update_source_configs()

    def set_initial_offset(self):
        source_config = self.client_config['source']['config']

        timestamp = datetime.now() - timedelta(days=int(self.client_config.get('initial_offset', 3)))
        if self.client_config['timestamp']['type'] == 'datetime':
            self.client_config['start'] = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        elif self.client_config['timestamp']['type'] == 'unix':
            self.client_config['start'] = str(int(timestamp.timestamp()))
        elif self.client_config['timestamp']['type'] == 'unix_ms':
            self.client_config['start'] = str(int(timestamp.timestamp() * 1e3))

        if self.client_config['offset_column'] == self.client_config['timestamp']['name']:
            source_config['initialOffset'] = self.client_config['start']
            return

        self.get_initial_offset_value_from_db()

    def get_initial_offset_value_from_db(self):
        source_config = self.client_config['source']['config']
        conn_info = urlparse(source_config['connection_string'])
        if source_config.get('hikariConfigBean.useCredentials'):
            userpass = source_config['hikariConfigBean.username'] + ':' + source_config['hikariConfigBean.password']
            netloc = userpass + '@' + conn_info.netloc
        else:
            netloc = conn_info.netloc

        scheme = conn_info.scheme + '+mysqlconnector' if self.client_config['source']['type'] == 'mysql' else conn_info.scheme
        try:
            eng = create_engine(urlunparse((scheme, netloc, conn_info.path, '', '', '')))
            with eng.connect() as con:
                result = con.execute("""SELECT {offset}, {timestamp} FROM {table} 
                                    WHERE {timestamp} <= '{start}' ORDER BY {offset} DESC LIMIT 1""".format(
                                        table=self.client_config['table'],
                                        offset=self.client_config['offset_column'],
                                        timestamp=self.client_config['timestamp']['name'],
                                        start=self.client_config['start']
                                    ))

                res = result.fetchone()
                source_config['initialOffset'] = str(res[0]) if res else '0'
        except SQLAlchemyError as e:
            raise ConfigHandlerException(str(e))
