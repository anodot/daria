import os
import re
import rrdtool
import tarfile

from typing import List
from agent.data_extractor import cacti
from agent.pipeline import Pipeline
from agent import source
from agent.modules import logger

logger_ = logger.get_logger(__name__)


class Source:
    def __init__(self, data: dict):
        self.name = data['name']
        self.name_cache = data['name_cache']
        self.data_source_path = data['data_source_path']


def extract_metrics(pipeline_: Pipeline, start: str, end: str, step: str) -> list:
    _extract_rrd_archive(pipeline_)
    try:
        metrics = []
        for cacti_source in cacti.source_cacher.get_sources(pipeline_):
            base_metric = {
                'target_type': 'gauge',
                'properties': _extract_dimensions(cacti_source),
            }
            rrd_file_name = cacti_source.data_source_path
            if not rrd_file_name:
                continue

            if '<path_rra>/' not in rrd_file_name:
                logger_.warning(f'Path {rrd_file_name} does not contain "<path_rra>/", skipping')
                continue

            rrd_file_path = rrd_file_name.replace('<path_rra>', _get_tmp_rrd_dir(pipeline_))
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
                    metric['properties']['what'] = measurement_name.replace(".", "_").replace(" ", "_")
                    metric['value'] = value
                    metric['timestamp'] = timestamp
                    metrics.append(metric)
    finally:
        _clean_rrd_dir(pipeline_)
    return metrics


def _extract_rrd_archive(pipeline_: Pipeline):
    file_path = pipeline_.source.config[source.CactiSource.RRD_ARCHIVE_PATH]
    if not os.path.isfile(file_path):
        raise ArchiveNotExistsException()
    with tarfile.open(file_path, "r:gz") as tar:
        tar.extractall(path=_get_tmp_rrd_dir(pipeline_))


def _clean_rrd_dir(pipeline_: Pipeline):
    try:
        os.remove(_get_tmp_rrd_dir(pipeline_))
    except OSError as e:
        logger_.error(f"{e.filename} - {e.strerror}")


def _get_tmp_rrd_dir(pipeline_: Pipeline):
    return os.path.join('/tmp/cacti_rrd/', pipeline_.name)


def _extract_dimensions(cacti_source: Source) -> dict:
    dimensions = {}
    dimension_values = _extract_dimension_values(cacti_source.name, cacti_source.name_cache)
    if not dimension_values:
        return {}
    dimension_names = _extract_dimension_names(cacti_source.name)
    if not dimension_names:
        return {}
    for i, name in enumerate(dimension_names):
        value = dimension_values[i]
        if isinstance(name, str):
            name = name.replace(".", "_").replace(" ", "_")
        if isinstance(value, str):
            value = value.replace(".", "_").replace(" ", "_")
        dimensions[name] = value
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


class ArchiveNotExistsException(Exception):
    pass
