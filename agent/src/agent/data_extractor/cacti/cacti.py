import os
import re
import shutil
import rrdtool

from copy import deepcopy
from typing import List, Optional
from agent import source
from agent.data_extractor import cacti
from agent.data_extractor.cacti.cacher import CactiCache
from agent.data_extractor.rrd import rrd
from agent.pipeline import Pipeline
from agent.modules import logger, tools

logger_ = logger.get_logger(__name__)


def extract_metrics(pipeline_: Pipeline, start: str, end: str, step: str) -> list:
    _prepare_files(pipeline_)
    cache = _get_cache(pipeline_)

    metrics = []
    for local_graph_id, graph in cache.graphs.items():
        # Count sum of metrics with the same name if graph for item that have SIMILAR_DATA_SOURCES_NODUPS in cdef
        metrics_to_sum = {}
        for item_id, item in graph['items'].items():
            if not _is_appropriate_graph_type(item):
                continue

            result = _read_data_from_rrd(item['data_source_path'], start, end, step, pipeline_)
            if not result:
                continue

            base_metric = _build_base_metric(item, graph, cache, str(local_graph_id), pipeline_)
            if _should_sum_similar_items(item):
                metrics_to_sum[item['data_source_name']] = base_metric
                continue

            metrics += rrd.build_metrics(
                result,
                start,
                end,
                _should_convert_to_bits(item, pipeline_),
                base_metric,
                item['data_source_name'],
            )
        metrics += _sum_similar(graph['items'], metrics_to_sum, start, end, step, pipeline_)
    return metrics


def _read_data_from_rrd(data_source_path, start, end, step, pipeline_: Pipeline):
    if not data_source_path:
        return
    if '<path_rra>/' not in data_source_path:
        logger_.debug(f'Path {data_source_path} does not contain "<path_rra>/", skipping')
        return

    rrd_file_path = data_source_path.replace('<path_rra>', _get_source_dir(pipeline_))
    if not os.path.isfile(rrd_file_path):
        logger_.debug(f'File {rrd_file_path} does not exist')
        return

    if source.RRDSource.RRD_DIR_PATH in pipeline_.source.config:
        rrd_file_path = _copy_files_to_tmp_dir(pipeline_, rrd_file_path, data_source_path)

    result = rrdtool.fetch(rrd_file_path, 'AVERAGE', ['-s', start, '-e', end, '-r', step])

    if source.RRDSource.RRD_DIR_PATH in pipeline_.source.config:
        os.remove(rrd_file_path)

    if not result or not result[0]:
        return

    # result[0][2] - is the closest available step to the step provided in the fetch command
    # if they differ - skip the source as the desired step is not available for it
    if result[0][2] != int(step) and not pipeline_.dynamic_step:
        return
    return result


def _get_cache(pipeline_) -> CactiCache:
    cache = cacti.repository.get_cache(pipeline_)
    if cache is None:
        raise Exception('Cacti cache does not exist')
    return cache


def _is_appropriate_graph_type(item: dict) -> bool:
    # 4, 5, 6, 7 ,8 are ids of AREA, STACK, LINE1, LINE2, and LINE3 graph item types
    return item['graph_type_id'] in [4, 5, 6, 7, 8]


def _build_base_metric(item: dict, graph: dict, cache: CactiCache, local_graph_id: str, pipeline_: Pipeline) -> dict:
    return {
        'target_type': 'gauge',
        'properties': _extract_dimensions(
            item,
            graph,
            cache.hosts,
            str(local_graph_id),
            pipeline_.config['add_graph_name_dimension'],
            pipeline_.config['add_graph_id_dimension'],
        ),
    }


def _get_data_to_sum(items: dict, metrics_to_sum: dict, start, end, step, pipeline_: Pipeline) -> list:
    data = []
    extracted_sources = set()
    for item in items.values():
        if item['data_source_name'] not in metrics_to_sum:
            continue
        key = item['data_source_path'] + '_' + item['data_source_name']
        if key in extracted_sources:
            continue
        # todo why do we read the file two times? We already read it once in extract_metrics() and here we do the same
        result = _read_data_from_rrd(item['data_source_path'], start, end, step, pipeline_)
        if not result:
            continue

        data += rrd.build_metrics(
            result,
            start,
            end,
            _should_convert_to_bits(item, pipeline_),
            metrics_to_sum[item['data_source_name']],
            item['data_source_name'],
        )
        extracted_sources.add(key)

    return data


def _sum_similar(items: dict, metrics_to_sum: dict, start, end, step, pipeline_: Pipeline) -> list:
    if not metrics_to_sum:
        return []

    result = {}
    for metric in _get_data_to_sum(items, metrics_to_sum, start, end, step, pipeline_):
        key = metric['properties']['what'] + '_' + str(metric['timestamp'])
        if key in result:
            result[key]['value'] += metric['value']
            continue
        result[key] = deepcopy(metrics_to_sum[metric['properties']['what']])
        result[key]['properties']['what'] = metric['properties']['what']
        result[key]['value'] = metric['value']
        result[key]['timestamp'] = metric['timestamp']

    return list(result.values())


def _extract_dimensions(
        item: dict,
        graph: dict,
        hosts: dict,
        local_graph_id: str,
        add_graph_name_dimension=False,
        add_graph_id_dimension=False,
) -> dict:
    host = _get_host(graph, hosts)
    dimensions = _extract_title_dimensions(graph['title'], graph, host)

    if add_graph_name_dimension:
        dimensions = _add_graph_name_dimension(dimensions, graph['title'])
    if add_graph_id_dimension:
        dimensions['graph_id'] = local_graph_id
    if 'host_description' not in dimensions and 'description' in host:
        dimensions['host_description'] = host['description']

    dimensions = {**dimensions, **_extract_item_dimensions(item, host)}

    return dimensions


def _add_graph_name_dimension(dimensions: dict, graph_title: str) -> dict:
    for k, v in dimensions.items():
        graph_title = graph_title.replace(f'|{k}|', v.strip())
    dimensions['graph_title'] = graph_title
    return dimensions


def _extract_title_dimensions(graph_title: str, graph: dict, host: dict) -> dict:
    dimensions = {}
    for var in _extract_dimension_names(graph_title):
        value = _extract(var, graph.get('variables', {}), host)
        if value is None or value == '':
            continue
        dimensions[var] = value
    return dimensions


def _get_host(graph, hosts):
    # if the host_id is 0 it means the graph doesn't have a host and it will not be used later
    return hosts[graph['host_id']] if graph['host_id'] != '0' else {}


def _extract(variable: str, variables: dict, host: dict) -> Optional[str]:
    if variable.startswith('host_'):
        prefix = 'host_'
        vars_ = host
    elif variable.startswith('query_'):
        prefix = 'query_'
        vars_ = variables
    else:
        return None
    var_name = variable.replace(prefix, '')
    if var_name not in vars_:
        return None
    return vars_[var_name]


def _extract_dimension_names(name: str) -> List[str]:
    # extract all values between `|`
    return re.findall('\|([^|]+)\|', name)


def _extract_item_dimensions(item: dict, host: dict) -> dict:
    dimensions = {}
    item_title = item['item_title']
    if 'variables' in item and item_title != '':
        for dimension_name in _extract_dimension_names(item_title):
            value = _extract(dimension_name, item['variables'], host)
            if value is None or value == '':
                continue
            dimensions[dimension_name] = value
    if item_title != '':
        for k, v in dimensions.items():
            item_title = item_title.replace(f'|{k}|', v)
        dimensions['item_title'] = item_title
    return dimensions


def _should_convert_to_bits(item: dict, pipeline_: Pipeline) -> bool:
    # the table cdef_items contains a list of functions that will be applied to a graph item
    # we need to find if there's a function that converts values to bits. We can find it out by checking two things:
    # 1. Either a function description, which is a string, contains "8,*", which means multiply by 8
    # 2. Or the function will have two sequential items with values 8 and 3. In this case 3 also means multiplication
    # also we assume cdef_items are ordered by `sequence`

    if not pipeline_.config['convert_bytes_into_bits'] or 'cdef_items' not in item:
        return False

    contains_8 = False
    for value in item['cdef_items'].values():
        if "8,*" in value:
            return True
        if str(value) == '8':
            contains_8 = True
        elif contains_8 and str(value) == '3':
            return True
        else:
            contains_8 = False


def _should_sum_similar_items(item: dict) -> bool:
    if 'cdef_items' not in item:
        return False
    return any(
        'SIMILAR_DATA_SOURCES_NODUPS' in value
        for value in item['cdef_items'].values()
    )


def _prepare_files(pipeline_):
    if source.RRDSource.RRD_ARCHIVE_PATH in pipeline_.source.config:
        tools.extract_archive(
            pipeline_.source.config[source.RRDSource.RRD_ARCHIVE_PATH],
            rrd.get_tmp_dir(pipeline_)
        )


def _get_source_dir(pipeline_: Pipeline) -> str:
    if source.RRDSource.RRD_DIR_PATH in pipeline_.source.config:
        return pipeline_.source.config[source.RRDSource.RRD_DIR_PATH]
    return rrd.get_tmp_dir(pipeline_)


def _copy_files_to_tmp_dir(pipeline_: Pipeline, old_path, data_source_path) -> str:
    tmp_dir = rrd.get_tmp_dir(pipeline_)
    new_path = data_source_path.replace('<path_rra>', tmp_dir)
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    shutil.copyfile(old_path, new_path)
    return new_path
