from datetime import datetime
from agent import pipeline, source, destination
from agent.modules import db
from agent.modules.logger import get_logger

logger = get_logger(__name__, stdout=True)

for pipeline_ in pipeline.repository.get_all():
    pipeline_.created_at = datetime.now()
    pipeline.repository.save(pipeline_)
    logger.info(f'Updated created_at column for pipeline ID = {pipeline_.id}')

for source_ in source.repository.get_all():
    source_.created_at = datetime.now()
    source.repository.save(source_)
    logger.info(f'Updated created_at column for source ID = {source_.id}')

destination_ = destination.repository.get()
destination_.created_at = datetime.now()
destination.repository.save(destination_)
logger.info(f'Updated created_at column for destination')
# todo this is temporary
db.session().commit()
db.session().close()
