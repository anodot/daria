from typing import Dict, List
from agent import pipeline
from agent.modules.streamsets import StreamSetsApiClient, StreamSets
from agent.modules import streamsets
from agent.pipeline import Pipeline

_clients: Dict[int, StreamSetsApiClient] = {}


def get_api_client_by_id(pipeline_id: str) -> StreamSetsApiClient:
    return get_api_client(pipeline.repository.get_by_name(pipeline_id))


def get_api_client(pipeline_: Pipeline) -> StreamSetsApiClient:
    global _clients
    if pipeline_.streamsets.id not in _clients:
        _clients[pipeline_.streamsets.id] = StreamSetsApiClient(pipeline_.streamsets)
    return _clients[pipeline_.streamsets.id]


def choose_streamsets() -> StreamSets:
    # choose streamsets with the lowest number of pipelines
    pipeline_streamsets = pipeline.repository.count_by_streamsets()
    streamsets_ = streamsets.repository.get_all()

    def foo(s: StreamSets):
        if s.id not in pipeline_streamsets:
            pipeline_streamsets[s.id] = 0

    map(foo, streamsets_)
    id_ = min(pipeline_streamsets, key=pipeline_streamsets.get)
    return streamsets.repository.get(id_)


def get_all_pipelines() -> List[dict]:
    pipelines = []
    for streamsets_ in streamsets.repository.get_all():
        client = StreamSetsApiClient(streamsets_)
        pipelines.append(client.get_pipelines())
    return pipelines


def get_all_pipeline_statuses() -> dict:
    # todo show streamsets id?
    statuses = {}
    for streamsets_ in streamsets.repository.get_all():
        client = StreamSetsApiClient(streamsets_)
        statuses = {**statuses, **client.get_pipelines_status()}
    return statuses


def get_streamsets_without_monitoring() -> List[StreamSets]:
    pipeline_streamsets_ids = set(map(
        lambda p: p.streamsets_id,
        pipeline.repository.get_all(),
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
