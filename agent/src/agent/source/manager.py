from agent import pipeline
from agent import source
from agent.source import SourceException, Source
from agent.modules.logger import get_logger


logger_ = get_logger(__name__, stdout=True)


def create_source_obj(source_name: str, source_type: str) -> Source:
    return source.types[source_type](source_name, source_type, {})


def update(source_: Source):
    if not source.repository.is_modified(source_):
        logger_.info(f'No need to update source {source_.name}')
        return

    source.validator.validate(source_)
    source.repository.save(source_)
    # todo remove this last dependency on the pipeline, implement observer?
    pipeline.manager.update_source_pipelines(source_)
    logger_.info(f'Saved source {source_.name}')


def get_previous_source_config(source_type):
    source_ = source.repository.get_last_edited(source_type)
    if source_:
        return source_.config
    return {}


def check_source_name(source_name: str):
    if source.repository.exists(source_name):
        raise SourceException(f"Source {source_name} already exists")


def delete(source_: Source):
    source.repository.delete(source_)
