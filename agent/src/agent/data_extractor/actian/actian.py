import pyodbc
from agent import source
from agent.pipeline import Pipeline
from agent.modules import logger

logger_ = logger.get_logger(__name__)


def extract_metrics(pipeline_: Pipeline, offset: int) -> list:
    cnx = pyodbc.connect(pipeline_.source.config[source.ActianSource.CONNECTION_STRING])
    cursor = cnx.cursor()
    timestamp_to_unix = f'UNIX_TIMESTAMP({pipeline_.timestamp_path})'
    timestamp_condition = f'{timestamp_to_unix} >= {offset} AND {timestamp_to_unix} < {offset} + {pipeline_.interval}'
    query = pipeline_.query.replace('{TIMESTAMP_CONDITION}', timestamp_condition)
    logger_.info(f'Executing query: {query}')
    cursor.execute(query)
    rows = cursor.fetchall()
    column_names = [c[0] for c in cursor.description]
    return [{c: row.__getattribute__(c) for c in column_names} for row in rows]


