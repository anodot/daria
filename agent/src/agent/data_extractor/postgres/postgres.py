import psycopg2
import psycopg2.extras
from agent import source
from agent.pipeline import Pipeline, TimestampType
from agent.modules import logger

logger_ = logger.get_logger(__name__)


def extract_metrics(pipeline_: Pipeline, offset: int) -> list:
    cnx = psycopg2.connect(pipeline_.source.config[source.PostgresPySource.CONNECTION_STRING])
    cursor = cnx.cursor(cursor_factory=psycopg2.extras.DictCursor)
    timestamp_condition = f'{pipeline_.timestamp_path} >= {offset} AND {pipeline_.timestamp_path} < {offset} + {pipeline_.interval}'
    query = pipeline_.query.replace('{TIMESTAMP_CONDITION}', timestamp_condition)
    logger_.info(f'Executing query: {query}')
    cursor.execute(query)
    return [dict(row) for row in cursor]


