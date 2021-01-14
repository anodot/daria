from agent import pipeline, source
from agent.modules import db, logger

logger_ = logger.get_logger(__name__, stdout=True)

SOURCE_NAME = 'monitoring'
for pipeline_ in pipeline.repository.get_by_source(SOURCE_NAME):
    pipeline.manager.delete(pipeline_)
    logger_.info(f'Pipeline {pipeline_.name} deleted')

source.manager.delete(source.repository.get_by_name(SOURCE_NAME))
logger_.info(f'{SOURCE_NAME} source deleted')

# todo this is temporary
db.session().commit()
db.session().close()
