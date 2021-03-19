import os
import re
import rrdtool

from typing import List
from . import repository
from agent.pipeline import Pipeline
from agent import source
from agent.modules import logger

logger_ = logger.get_logger(__name__)


def extract_metrics(pipeline_: Pipeline, start: str, end: str, step: str) -> list:
    metrics = []

    sources = repository.get_cacti_sources(
        pipeline_.source.config[source.CactiSource.MYSQL_CONNECTION_STRING],
        pipeline_.config.get('exclude_hosts'),
        pipeline_.config.get('exclude_datasources')
    )
    for cacti_source in sources:
        dimensions = _extract_dimensions(cacti_source)
        if not dimensions:
            continue
        base_metric = {
            'target_type': 'gauge',
            'properties': dimensions,
        }
        rrd_file_name = cacti_source['data_source_path']
        if not rrd_file_name:
            continue

        if '<path_rra>' not in rrd_file_name:
            logger_.warning(f'Path {rrd_file_name} does not contain "<path_rra>/", skipping')
            continue

        rrd_file_path = rrd_file_name.replace('<path_rra>', pipeline_.source.config[source.CactiSource.RRD_DIR])
        if not os.path.isfile(rrd_file_path):
            logger_.warning(f'File {rrd_file_path} does not exist')
            continue
        result = rrdtool.fetch(rrd_file_path, 'AVERAGE', ['-s', start, '-e', end, '-r', step])

        # result[0][2] - is the closest available step to the step provided in the fetch command
        # if they differ - skip the source as the desired step is not available in it
        if result[0][2] != int(step):
            continue

        # contains the timestamp of the first data item
        data_start = result[0][0]
        for name_idx, measurement_name in enumerate(result[1]):
            for row_idx, data in enumerate(result[2]):
                timestamp = int(data_start) + row_idx * int(step)
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
                metric['what'] = measurement_name
                metric['value'] = value
                metric['timestamp'] = timestamp
                metrics.append(metric)
    return metrics


def _extract_dimensions(cacti_source: dict) -> dict:
    source_name = cacti_source['name']
    dimensions = {}
    dimension_values = _extract_dimension_values(source_name, cacti_source['name_cache'])
    if not dimension_values:
        logger_.warning(f'Failed to extract dimension values from {source_name}, skipping')
        return {}
    dimension_names = _extract_dimension_names(source_name)
    if not dimension_names:
        logger_.warning(f'Failed to extract dimension names from {source_name}, skipping')
        return {}
    for i, name in enumerate(dimension_names):
        dimensions[name] = dimension_values[i]

    return dimensions


def _extract_dimension_names(name: str) -> List[str]:
    # extract all values between `|`
    return re.findall('\|([^|]+)\|', name)


def _extract_dimension_values(name: str, name_cache: str) -> List[tuple]:
    regex = re.sub('(\|[^|]+\|)', '(.*)', name)
    result = re.findall(regex, name_cache)
    if not result:
        return []
    return list(result[0])
