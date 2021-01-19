import sdc_client

from agent import pipeline, streamsets
from agent.modules.logger import get_logger
from agent.streamsets import StreamSets

logger = get_logger(__name__, stdout=True)


def create_streamsets(streamsets_: StreamSets):
    streamsets.repository.save(streamsets_)


def delete_streamsets(streamsets_: StreamSets):
    if _has_pipelines(streamsets_):
        if not _can_move_pipelines():
            raise StreamsetsException(
                'Cannot move pipelines to a different streamsets as only one streamsets instance exists, cannot delete streamsets that has pipelines'
            )
        sdc_client.StreamsetsBalancer().unload_streamsets(streamsets_)
    streamsets.repository.delete(streamsets_)


def _has_pipelines(streamsets_: StreamSets) -> bool:
    return len(pipeline.repository.get_by_streamsets_id(streamsets_.id)) > 0


def _can_move_pipelines():
    return len(streamsets.repository.get_all()) > 1


class StreamsetsException(Exception):
    pass

# TODO: pass StreamSets instance as an argument
