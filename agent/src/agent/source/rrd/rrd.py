import os
import re
import rrdtool

from typing import List
from . import repository
from agent.modules import logger
from agent.source import Source

logger_ = logger.get_custom_logger(__name__, os.environ.get('RRD_SOURCE_LOG_FILE_PATH', 'agent_rrd_source.log'))


def extract_metrics(
    source_: Source, start: str, end: str, step: str,
    *, exclude_hosts: list, exclude_datasources: list
) -> list:
    # todo if average function is not available in the rrd - skip this source
    metrics = []

    for cacti_source in repository.get_cacti_sources(source_, exclude_hosts, exclude_datasources):
        base_metric = {
            'target_type': 'gauge',
            'properties': _extract_dimensions(cacti_source),
        }
        rrd_file_name = _extract_rrd_file_name(cacti_source)
        if not rrd_file_name:
            continue
        rrd_file_path = os.path.join(source_.get_rrd_dir(), rrd_file_name)
        rrd_file_path = '/Users/antonzelenin/Workspace/daria/agent/src/agent/data.rrd'
        info = rrdtool.info(rrd_file_path)
        res = rrdtool.fetch(rrd_file_path, 'AVERAGE', ['-s', start, '-e', end, '-r', step])
        # res[0][2] - is the closest available step to the step provided in the fetch command
        # if they differ - skip the source as the desired step is not available in it
        if res[0][2] != int(step):
            continue

        for name_idx, measurement_name in enumerate(res[1]):
            def produce_metric(row_idx: int, values: tuple) -> dict:
                metric = base_metric.copy()
                metric['what'] = measurement_name
                metric['value'] = values[name_idx]
                metric['timestamp'] = int(start) + row_idx * int(step)
                return metric

            metrics.extend([produce_metric(row_idx, data) for row_idx, data in enumerate(res[2])])

    return metrics


def _extract_dimensions(cacti_source: dict) -> dict:
    dimensions = {}

    dimension_values = _extract_dimension_values(cacti_source['name'], cacti_source['name_cache'])
    for i, name in enumerate(_extract_dimension_names(cacti_source['name'])):
        dimensions[name] = dimension_values[i]

    return dimensions


def _extract_rrd_file_name(cacti_source: dict) -> str:
    path = cacti_source['data_source_path']
    # every data source path starts with '<path_rra>/' so removing it
    return path[len('<path_rra>/'):]


def _extract_dimension_names(name: str) -> List[str]:
    # extract all values between `|`
    return re.findall('\|([^|]+)\|', name)


def _extract_dimension_values(name: str, name_cache: str) -> List[tuple]:
    reg = re.sub('(\|[^|]+\|)', '(.*)', name)
    # todo can it return more than one group?
    return list(re.findall(reg, name_cache)[0])
