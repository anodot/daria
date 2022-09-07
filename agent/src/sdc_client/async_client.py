import json
import time
import inject
import asyncio

from typing import List, Dict, Tuple
from sdc_client import force_stop, StreamsetsException
from sdc_client.async_api_client import _AsyncClientsManager, _AsyncStreamSetsApiClient
from sdc_client.interfaces import ILogger, IStreamSets, IPipeline

_clients_async: Dict[int, _AsyncStreamSetsApiClient] = {}


def _client_async(pipeline: IPipeline) -> _AsyncStreamSetsApiClient:
    if not pipeline.get_streamsets():
        raise StreamsetsException(f'Pipeline `{pipeline.get_id()}` does not belong to any StreamSets')
    if pipeline.get_streamsets().get_id() not in _clients_async:
        _clients_async[pipeline.get_streamsets().get_id()] = _AsyncStreamSetsApiClient(pipeline.get_streamsets())
    return _clients_async[pipeline.get_streamsets().get_id()]


def _get_async_client(streamsets: IStreamSets) -> _AsyncStreamSetsApiClient:
    global _clients_async
    if streamsets.get_id() not in _clients_async:
        _clients_async[streamsets.get_id()] = _AsyncStreamSetsApiClient(streamsets)
    return _clients_async[streamsets.get_id()]


def _get_async_client_from_pipelines(pipelines: List[IPipeline]) -> List[_AsyncStreamSetsApiClient]:
    return [_get_async_client(streamsets) for streamsets in {pipeline.get_streamsets() for pipeline in pipelines}]


def get_jmxes_async(queries: List[Tuple[IStreamSets, str]], return_exceptions=False) -> List[Dict]:
    async def execute_requests(queries_: List[Tuple[IStreamSets, str]]):
        clients = [_get_async_client(ss) for ss in {ss for ss, _ in queries_}]
        async with _AsyncClientsManager(clients) as manager:
            return await asyncio.gather(
                *[asyncio.create_task(manager.clients[streamset_.get_id()].get_jmx(query)) for streamset_, query in queries],
                return_exceptions=return_exceptions
            )
    return asyncio.run(execute_requests(queries))


async def get_pipeline_statuses_async(pipelines: List[IPipeline], return_exceptions=False):
    streamsets_ = list({pipeline.get_streamsets() for pipeline in pipelines})
    clients = [_get_async_client(ss) for ss in streamsets_]
    async with _AsyncClientsManager(clients) as manager:
        return await asyncio.gather(
            *[asyncio.create_task(manager.clients[ss.get_id()].get_pipeline_statuses()) for ss in streamsets_],
            return_exceptions=return_exceptions
        )


async def start_async(pipelines: List[IPipeline], return_exceptions=False):
    clients = _get_async_client_from_pipelines(pipelines)
    async with _AsyncClientsManager(clients) as manager:
        return await asyncio.gather(
            *[asyncio.create_task(manager.clients[pipeline.get_streamsets().get_id()].start_pipeline(pipeline.get_id()))
              for pipeline in pipelines],
            return_exceptions=return_exceptions
        )


async def stop_async(pipelines: List[IPipeline], return_exceptions=False):
    clients = _get_async_client_from_pipelines(pipelines)
    async with _AsyncClientsManager(clients) as manager:
        return await asyncio.gather(
            *[asyncio.create_task(manager.clients[pipeline.get_streamsets().get_id()].stop_pipeline(pipeline.get_id()))
              for pipeline in pipelines],
            return_exceptions=return_exceptions
        )


async def delete_async(pipelines: List[IPipeline], return_exceptions=False):
    clients = _get_async_client_from_pipelines(pipelines)
    async with _AsyncClientsManager(clients) as manager:
        return await asyncio.gather(
            *[asyncio.create_task(manager.clients[pipeline.get_streamsets().get_id()].delete_pipeline(pipeline.get_id()))
              for pipeline in pipelines],
            return_exceptions=return_exceptions
        )


async def create_async(pipelines: List[IPipeline], return_exceptions=False):
    clients = _get_async_client_from_pipelines(pipelines)
    async with _AsyncClientsManager(clients) as manager:
        return await asyncio.gather(
            *[asyncio.create_task(manager.clients[pipeline.get_streamsets().get_id()].create_pipeline(pipeline.get_id()))
              for pipeline in pipelines],
            return_exceptions=return_exceptions
        )


async def set_offsets_async(pipelines: List[IPipeline], return_exceptions=False):
    clients = _get_async_client_from_pipelines(pipelines)
    async with _AsyncClientsManager(clients) as manager:
        return await asyncio.gather(
            *[asyncio.create_task(manager.clients[pipeline.get_streamsets().get_id()].post_pipeline_offset(pipeline.get_id(), json.loads(pipeline.get_offset())))
              for pipeline in pipelines if pipeline.get_offset()],
            return_exceptions=return_exceptions
        )


async def get_pipelines_async(pipelines: List[IPipeline], return_exceptions=False):
    clients = _get_async_client_from_pipelines(pipelines)
    async with _AsyncClientsManager(clients) as manager:
        return await asyncio.gather(
            *[asyncio.create_task(manager.clients[pipeline.get_streamsets().get_id()].get_pipeline(pipeline.get_id()))
              for pipeline in pipelines],
            return_exceptions=return_exceptions
        )


async def update_pipeline_async(pipelines: List[IPipeline], configs: List[Dict], return_exceptions=False):
    clients = _get_async_client_from_pipelines(pipelines)
    async with _AsyncClientsManager(clients) as manager:
        return await asyncio.gather(
            *[asyncio.create_task(manager.clients[pipeline.get_streamsets().get_id()].update_pipeline(pipeline.get_id(), config))
              for pipeline, config in zip(pipelines, configs)],
            return_exceptions=return_exceptions
        )


def _update_pipelines_async(pipelines: List[IPipeline], set_offset: bool = False):
    if set_offset:
        asyncio.run(set_offsets_async(pipelines))
    new_configs = [pipeline.get_streamsets_config() for pipeline in pipelines]
    old_configs = asyncio.run(get_pipelines_async(pipelines))
    for config in new_configs:
        new_uuid = [old_config['uuid'] for old_config in old_configs if config['title'] == old_config['title']][0]
        config['uuid'] = new_uuid
    asyncio.run(update_pipeline_async(pipelines, new_configs))


def _stop_running(pipelines: List[IPipeline]) -> List[IPipeline]:
    pipelines_info = asyncio.run(get_pipeline_statuses_async(pipelines))
    pipeline_statuses = {pipeline.get_id(): pipelines_info[0][pipeline.get_id()]['status'] for pipeline in pipelines}
    pipelines_running = [p for p in pipelines if pipeline_statuses[p.get_id()] in
                         (IPipeline.STATUS_RUNNING, IPipeline.STATUS_STARTING, IPipeline.STATUS_RETRY)]
    try:
        asyncio.run(stop_async(pipelines_running))
        time.sleep(2)
    except Exception as e:
        inject.instance(ILogger).debug(f'Could not stop pipelines {[p.get_id() for p in pipelines]} asynchronously: {str(e)}')
        for pipeline in pipelines:
            force_stop(pipeline)
    return pipelines_running


def update_async(pipelines: List[IPipeline]):
    try:
        pipelines_running = _stop_running(pipelines)
        _update_pipelines_async(pipelines)
        asyncio.run(start_async(pipelines_running))
    except Exception as e:
        raise StreamsetsException(f'Pipelines could not be updated due to the errors: {str(e)}') from e


def move_to_streamsets_async(rebalance_map: Dict[IPipeline, IStreamSets]):
    pipelines = list(rebalance_map)
    try:
        pipelines_running = _stop_running(pipelines)
        asyncio.run(delete_async(pipelines))
        for pipeline_, streamsets_ in rebalance_map.items():
            pipeline_.set_streamsets(streamsets_)
        asyncio.run(create_async(pipelines))
        _update_pipelines_async(pipelines, set_offset=True)
        asyncio.run(start_async(pipelines_running))
    except Exception as e:
        raise StreamsetsException(f'StreamSets could not be balanced due to the errors: {str(e)}') from e

