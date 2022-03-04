import os
import shutil
import rrdtool

from copy import deepcopy
from agent import source
from agent.pipeline import Pipeline
from agent.modules import logger, tools

RRD_TMP_DIR = '/tmp/rrd/'

logger_ = logger.get_logger(__name__)


def extract_metrics(pipeline_: Pipeline, start: str, end: str, step: str) -> list:
    with TMPDir(pipeline_) as rrd_dir_path:
        metrics = []
        for file in tools.get_all_files(rrd_dir_path):
            if not file.endswith('.rrd'):
                logger_.info(f'Skipping file `{file}`')
                continue
            res = read_data_from_rrd(os.path.join(rrd_dir_path, file), start, end, step, pipeline_)
            base_metric = _get_base_metric(file.replace(get_tmp_dir(pipeline_) + '/', ''))
            metrics.extend(build_metrics(res, start, end, False, base_metric))
    return metrics


def _get_base_metric(file: str) -> dict:
    return {
        'target_type': 'gauge',
        'properties': {
            'data_source': file,
        },
    }


def _build_base_metric() -> dict:
    return {
        'target_type': 'gauge',
        'properties': {

        }
    }


def read_data_from_rrd(rrd_file_path: str, start, end, step, pipeline_: Pipeline):
    if not os.path.isfile(rrd_file_path):
        logger_.error(f'File {rrd_file_path} does not exist')
        return

    result = rrdtool.fetch(rrd_file_path, 'AVERAGE', ['-s', start, '-e', end, '-r', step])

    if not result or not result[0]:
        logger_.debug(f'No data found for the rrd file `{rrd_file_path}`')
        return

    # result[0][2] - is the closest available step to the step provided in the fetch command
    # if they differ - skip the source as the desired step is not available for it
    if result[0][2] != int(step) and not pipeline_.dynamic_step:
        return
    return result


def get_tmp_dir(pipeline_: Pipeline):
    return os.path.join(RRD_TMP_DIR, pipeline_.name)


def build_metrics(
        rrd_result,
        start: str,
        end: str,
        should_convert_to_bits: bool,
        base_metric: dict,
        filter_measurement: str = None,
) -> list:
    values = []
    first_data_item_timestamp = rrd_result[0][0]
    for name_idx, measurement_name in enumerate(rrd_result[1]):
        if filter_measurement and measurement_name != filter_measurement:
            continue
        for row_idx, data in enumerate(rrd_result[2]):
            timestamp = int(first_data_item_timestamp) + row_idx * int(rrd_result[0][2])
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

            if should_convert_to_bits:
                value *= 8

            metric = deepcopy(base_metric)
            metric['properties']['what'] = measurement_name
            metric['value'] = value
            metric['timestamp'] = timestamp
            values.append(metric)
    return values


class TMPDir:
    def __init__(self, pipeline_: Pipeline):
        self.pipeline = pipeline_
        self.tmp_dir = get_tmp_dir(pipeline_)

    def __enter__(self):
        if source.RRDSource.RRD_ARCHIVE_PATH in self.pipeline.source.config:
            tools.extract_archive(
                self.pipeline.source.config[source.RRDSource.RRD_ARCHIVE_PATH],
                self.tmp_dir,
                self.pipeline.config['archive_compression'],
            )
        else:
            tools.copy_dir(
                self.pipeline.source.config[source.RRDSource.RRD_DIR_PATH],
                self.tmp_dir,
            )
        return self.tmp_dir

    def __exit__(self, exc_type, exc_value, exc_traceback):
        shutil.rmtree(self.tmp_dir)
