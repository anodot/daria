from agent import pipeline, source, di
from agent.modules import db, logger

logger_ = logger.get_logger(__name__, stdout=True)
di.init()

SOURCE_NAME = 'monitoring'
for pipeline_ in pipeline.repository.get_by_source(SOURCE_NAME):
    pipeline.manager.delete(pipeline_)
    logger_.info(f'Pipeline {pipeline_.name} deleted')

source_ = db.Session.query(source.Source).filter(source.Source.name == SOURCE_NAME).first()
source.repository.delete(source_)
logger_.info(f'{SOURCE_NAME} source deleted')
