import os
import re
import rrdtool
import tarfile

from typing import List, Optional
from agent.data_extractor.cacti.source_cacher import CactiCacher
from agent.pipeline import Pipeline
from agent import source
from agent.modules import logger

logger_ = logger.get_logger(__name__)


def extract_metrics(pipeline_: Pipeline, start: str, end: str, step: str) -> list:
    if pipeline_.source.RRD_ARCHIVE_PATH in pipeline_.source.config:
        _extract_rrd_archive(pipeline_)

    cacher = CactiCacher(pipeline_)
    variables = cacher.variables
    graphs = cacher.graphs
    hosts = cacher.hosts

    metrics = []
    for local_graph_id, rrd_file_name in cacher.sources.items():
        if local_graph_id not in graphs:
            logger_.warning(f'local_graph_id `{local_graph_id}` is not in a list of graphs, skipping')
            continue
        if local_graph_id not in variables:
            logger_.warning(f'local_graph_id `{local_graph_id}` is not in a list of variables, skipping')
            continue
        if not rrd_file_name:
            continue
        if '<path_rra>/' not in rrd_file_name:
            logger_.warning(f'Path {rrd_file_name} does not contain "<path_rra>/", skipping')
            continue
        rrd_file_path = rrd_file_name.replace('<path_rra>', _get_rrd_dir(pipeline_))
        if not os.path.isfile(rrd_file_path):
            logger_.warning(f'File {rrd_file_path} does not exist')
            continue

        base_metric = {
            'target_type': 'gauge',
            'properties': _extract_dimensions(
                graphs[local_graph_id],
                variables[local_graph_id],
                hosts[str(variables[local_graph_id]['host_id'])],
                pipeline_.config['add_graph_name_dimension']
            ),
        }

        result = rrdtool.fetch(rrd_file_path, 'AVERAGE', ['-s', start, '-e', end, '-r', step])

        # result[0][2] - is the closest available step to the step provided in the fetch command
        # if they differ - skip the source as the desired step is not available for it
        if result[0][2] != int(step):
            continue

        first_data_item_timestamp = result[0][0]
        for name_idx, measurement_name in enumerate(result[1]):
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

                metric = base_metric.copy()
                metric['properties']['what'] = measurement_name.replace(".", "_").replace(" ", "_")
                metric['value'] = value
                metric['timestamp'] = timestamp
                metrics.append(metric)
    return metrics


def _extract_dimensions(graph_title: str, variables: dict, host: dict, add_graph_name_dimension=False) -> dict:
    dimensions = {}
    for var in _extract_dimension_names(graph_title):
        value = _extract(var, variables, host)
        if value is None:
            logger_.warning(f'Variable `{var}` does not exist`')
            continue
        if value == '':
            logger_.warning(f'Value for `{var}` variable is empty, skipping')
            continue

        dimensions[var] = value
    if add_graph_name_dimension:
        for k, v in dimensions.items():
            graph_title = graph_title.replace(f'|{k}|', v)
        dimensions['graph_title'] = graph_title
    if 'host_description' not in dimensions:
        dimensions['host_description'] = host['description']
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


class ArchiveNotExistsException(Exception):
    pass
