from agent import pipeline, destination, source
from agent.modules import logger

logger_ = logger.get_logger(__name__, stdout=True)

for p in pipeline.repository.get_all():
    if p.source.type == source.TYPE_DIRECTORY:
        p.config['protocol'] = destination.HttpDestination.PROTOCOL_30
    else:
        p.config['protocol'] = destination.HttpDestination.PROTOCOL_20
    pipeline.repository.save(p)
    logger_.info(f'Pipeline `{p.name}` updated to use anodot protocol 2.0')
