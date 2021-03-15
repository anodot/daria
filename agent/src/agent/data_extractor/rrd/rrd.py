import re
import rrdtool

from typing import List
from . import repository
from agent.pipeline import Pipeline
from agent import source


def extract_metrics(pipeline_: Pipeline, start: str, end: str, step: str) -> list:
    metrics = []

    sources = repository.get_cacti_sources(
        pipeline_.source.config[source.CactiSource.MYSQL_CONNECTION_STRING],
        pipeline_.config.get('exclude_hosts'),
        pipeline_.config.get('exclude_datasources')
    )
    for cacti_source in sources:
        base_metric = {
            'target_type': 'gauge',
            'properties': _extract_dimensions(cacti_source),
        }
        rrd_file_name = cacti_source['data_source_path']
        if not rrd_file_name:
            continue

        rrd_file_path = rrd_file_name.replace('<path_rra>', pipeline_.source.config[source.CactiSource.RRD_DIR])
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
    dimensions = {}

    dimension_values = _extract_dimension_values(cacti_source['name'], cacti_source['name_cache'])
    for i, name in enumerate(_extract_dimension_names(cacti_source['name'])):
        dimensions[name] = dimension_values[i]

    return dimensions


def _extract_dimension_names(name: str) -> List[str]:
    # extract all values between `|`
    return re.findall('\|([^|]+)\|', name)


def _extract_dimension_values(name: str, name_cache: str) -> List[tuple]:
    reg = re.sub('(\|[^|]+\|)', '(.*)', name)
    # todo can it return more than one group?
    return list(re.findall(reg, name_cache)[0])
