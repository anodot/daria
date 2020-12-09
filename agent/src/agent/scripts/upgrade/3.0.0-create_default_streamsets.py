from agent import streamsets, pipeline
from agent.modules import constants, db
from agent.streamsets import StreamSets, get_logger

logger = get_logger(__name__, stdout=True)


def create_streamsets():
    if len(streamsets.repository.get_all()) > 0:
        logger.info('You already have a streamsets instance in the db')
        exit(1)

    streamsets.repository.save(StreamSets(
        constants.DEFAULT_STREAMSETS_URL,
        constants.DEFAULT_STREAMSETS_USERNAME,
        constants.DEFAULT_STREAMSETS_PASSWORD,
        constants.AGENT_DEFAULT_URL,
    ))
    logger.info(f'Created streamsets `{constants.DEFAULT_STREAMSETS_URL}`')


def set_pipeline_streamsets():
    streamsets_ = streamsets.repository.get_all()[0]
    for p in pipeline.repository.get_all():
        p.set_streamsets(streamsets_)
        pipeline.repository.save(p)
        logger.info(f'Set streamsets for pipeline ID = {p.id}')


def update_monitoring():
    pipeline.manager.delete(
        pipeline.repository.get_by_name(pipeline.MONITORING)
    )
    pipeline.manager.create_monitoring_pipelines()


create_streamsets()
set_pipeline_streamsets()
update_monitoring()

# todo this is temporary
db.session().commit()
db.session().close()
