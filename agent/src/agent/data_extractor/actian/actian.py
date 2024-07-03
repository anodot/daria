import pyodbc
from agent import source
from agent.pipeline import Pipeline
from agent.modules import logger

logger_ = logger.get_logger(__name__)


def extract_metrics(pipeline_: Pipeline, offset: int) -> list:
    cnx = pyodbc.connect(pipeline_.source.config[source.ActianSource.CONNECTION_STRING])
    cursor = cnx.cursor()
    cursor.execute(pipeline_.query)  # todo timestamp condtion replace
    rows = cursor.fetchall()
    column_names = [c[0] for c in cursor.description]
    return [row.__getattribute__(c) for c in column_names for row in rows]


