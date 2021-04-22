import os
import re
import rrdtool
import tarfile

from copy import deepcopy
from typing import List, Optional
from agent.data_extractor import cacti
from agent.pipeline import Pipeline
from agent import source
from agent.modules import logger

logger_ = logger.get_logger(__name__)


def extract_metrics(pipeline_: Pipeline, start: str, end: str, step: str) -> list:
    if pipeline_.source.RRD_ARCHIVE_PATH in pipeline_.source.config:
        _extract_rrd_archive(pipeline_)

    cache = cacti.repository.get_cache(pipeline_)
    if cache is None:
        cacti.cacher.cache_data()
        cache = cacti.repository.get_cache(pipeline_)

    metrics = []
    for local_graph_id, graph in cache.graphs.items():
        for item_id, item in graph['items'].items():
            data_source_path = item['data_source_path']
            if not data_source_path:
                continue
            if '<path_rra>/' not in data_source_path:
                logger_.debug(f'Path {data_source_path} does not contain "<path_rra>/", skipping')
                continue
            rrd_file_path = data_source_path.replace('<path_rra>', _get_rrd_dir(pipeline_))
            if not os.path.isfile(rrd_file_path):
                logger_.debug(f'File {rrd_file_path} does not exist')
                continue

            base_metric = {
                'target_type': 'gauge',
                'properties': _extract_dimensions(graph, cache.hosts, pipeline_.config['add_graph_name_dimension']),
            }

            result = rrdtool.fetch(rrd_file_path, 'AVERAGE', ['-s', start, '-e', end, '-r', step])

            # result[0][2] - is the closest available step to the step provided in the fetch command
            # if they differ - skip the source as the desired step is not available for it
            if result[0][2] != int(step):
                continue

            first_data_item_timestamp = result[0][0]
            for name_idx, measurement_name in enumerate(result[1]):
                if measurement_name != item['data_source_name']:
                    continue
                for row_idx, data in enumerate(result[2]):
                    timestamp = int(first_data_item_timestamp) + row_idx * int(step)
                    value = data[name_idx]

                    # rrd might return a record for the timestamp earlier then start
                    if timestamp < int(start):
                        continue
                    # skip values with timestamp end in order not to duplicate them
                    if timestamp >= int(end):
                        continue
                    # value will be None if it's not available for the chosen consolidation function or timestamp
                    if value is None:
                        continue

                    metric = deepcopy(base_metric)
                    metric['properties']['what'] = measurement_name.replace(".", "_").replace(" ", "_")
                    metric['value'] = value
                    metric['timestamp'] = timestamp
                    metrics.append(metric)
    return metrics


def _extract_dimensions(graph: dict, hosts: dict, add_graph_name_dimension=False) -> dict:
    dimensions = {}
    graph_title = graph['title']
    if graph['host_id'] != '0':
        host = hosts[graph['host_id']]
    else:
        # this means the graph doesn't have host and it will not be used later
        host = {}
    for var in _extract_dimension_names(graph_title):
        value = _extract(var, graph.get('variables', {}), host)
        if value is None:
            continue
        if value == '':
            continue

        dimensions[var] = value
    if add_graph_name_dimension:
        for k, v in dimensions.items():
            graph_title = graph_title.replace(f'|{k}|', v)
        dimensions['graph_title'] = graph_title
    if 'host_description' not in dimensions and 'description' in host:
        dimensions['host_description'] = host['description']

    for item_id, item in graph['items'].items():
        dimensions = {**dimensions, **_extract_item_dimensions(item)}

    return _replace_illegal_chars(dimensions)


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


def _replace_illegal_chars(dimensions: dict) -> dict:
    return {re.sub('\s+', '_', k.strip().replace(".", "_")): re.sub('\s+', '_', v.strip().replace(".", "_")) for k, v in dimensions.items()}


def _extract_rrd_archive(pipeline_: Pipeline):
    file_path = pipeline_.source.config[source.CactiSource.RRD_ARCHIVE_PATH]
    if not os.path.isfile(file_path):
        raise ArchiveNotExistsException()
    with tarfile.open(file_path, "r:gz") as tar:
        tar.extractall(path=_get_rrd_dir(pipeline_))


def _get_rrd_dir(pipeline_: Pipeline):
    if source.CactiSource.RRD_ARCHIVE_PATH in pipeline_.source.config:
        return os.path.join('/tmp/cacti_rrd/', pipeline_.name)
    else:
        return pipeline_.source.config[source.CactiSource.RRD_DIR_PATH]


def _extract_dimension_names(name: str) -> List[str]:
    # extract all values between `|`
    return re.findall('\|([^|]+)\|', name)


def _extract_item_dimensions(item: dict) -> dict:
    dimensions = {}
    item_title = item['item_title']
    for dimension_name in _extract_dimension_names(item_title):
        if not dimension_name.startswith('query'):
            continue
        dimension_name = dimension_name.replace('query_', '')
        if dimension_name not in item['variables']:
            continue
        dimensions[dimension_name] = item['variables'][dimension_name]

    dimensions['item_title'] = item_title
    return dimensions


class ArchiveNotExistsException(Exception):
    pass
