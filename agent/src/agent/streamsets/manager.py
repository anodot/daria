import sdc_client

from typing import List
from agent import pipeline, streamsets, destination
from agent.modules.logger import get_logger
from agent.streamsets import StreamSets

logger = get_logger(__name__, stdout=True)


def create_streamsets(streamsets_: StreamSets):
    streamsets.repository.save(streamsets_)
    if destination.repository.exists():
        pipeline.manager.create_monitoring_pipelines()


def delete_streamsets(streamsets_: StreamSets):
    if _has_pipelines(streamsets_):
        if not _can_move_pipelines():
            raise StreamsetsException(
                'Cannot move pipelines to a different streamsets as only one streamsets instance exists, cannot delete streamsets that has pipelines'
            )
        sdc_client.StreamsetsBalancer().unload_streamsets(streamsets_)
    pipeline.manager.delete_monitoring_pipeline(streamsets_)
    streamsets.repository.delete(streamsets_)


def _has_pipelines(streamsets_: StreamSets) -> bool:
    pipelines = pipeline.repository.get_by_streamsets_id(streamsets_.id)
    if len(pipelines) > 1:
        return True
    if len(pipelines) == 1 and not pipeline.manager.is_monitoring(pipelines[0]):
        return True
    return False


def _can_move_pipelines():
    return len(streamsets.repository.get_all()) > 1


def get_streamsets_without_monitoring() -> List[StreamSets]:
    pipeline_streamsets_ids = set(map(
        lambda p: p.streamsets_id,
        pipeline.repository.get_monitoring_pipelines(),
    ))
    streamsets_ = streamsets.repository.get_all()
    streamsets_ids = set(map(
        lambda s: s.id,
        streamsets_,
    ))
    without_monitoring = streamsets_ids - pipeline_streamsets_ids
    return list(filter(
        lambda s: s.id in without_monitoring,
        streamsets_
    ))


class StreamsetsException(Exception):
    pass
