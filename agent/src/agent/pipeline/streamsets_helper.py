from typing import Dict
from agent import pipeline
from agent.modules.streamsets import StreamSetsApiClient, StreamSets
from agent.modules import streamsets

_clients: Dict[int, StreamSetsApiClient] = {}


def get_api_client(pipeline_id: str) -> StreamSetsApiClient:
    global _clients
    pipeline_ = pipeline.repository.get_by_name(pipeline_id)
    if pipeline_.streamsets.id not in _clients:
        _clients[pipeline_.streamsets.id] = StreamSetsApiClient(pipeline_.streamsets)
    return _clients[pipeline_.streamsets.id]


def choose_streamsets() -> StreamSets:
    # choose streamsets with the lowest number of pipelines
    streamsets_ = pipeline.repository.count_by_streamsets()
    id_ = min(streamsets_, key=streamsets_.get)
    return streamsets.repository.get(id_)


def get_all_pipeline_statuses() -> dict:
    pass
