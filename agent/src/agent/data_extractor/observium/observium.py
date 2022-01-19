import time
import requests
import urllib.parse

from requests.auth import HTTPBasicAuth
from agent import source, monitoring
from agent.modules import logger, field, lookup
from agent.pipeline import Pipeline

logger_ = logger.get_logger(__name__)

N_REQUESTS_TRIES = 3

POLL_TIME_KEYS = {
    'ports': 'poll_time',
    'mempools': 'mempool_polled',
    'processors': 'processor_polled',
    'storage': 'storage_polled',
}

RESPONSE_DATA_KEYS = {
    'ports': 'ports',
    'mempools': 'entries',
    'processors': 'entries',
    'storage': 'storage',
}


def extract_metrics(pipeline_: Pipeline) -> list:
    with lookup.Provide(pipeline_.lookup):
        base_url = urllib.parse.urljoin(pipeline_.source.config[source.ObserviumSource.URL], '/api/v0/')
        endpoint = pipeline_.source.config['endpoint']
        data = _get(
            pipeline_,
            urllib.parse.urljoin(base_url, endpoint),
            pipeline_.config.get('request_params', {}),
            RESPONSE_DATA_KEYS[endpoint],
        )
        data = _add_devices_data(data, pipeline_)
        return _create_metrics(data, pipeline_)


def _get(pipeline_: Pipeline, url: str, params: dict, response_key: str):
    for i in range(1, N_REQUESTS_TRIES + 1):
        try:
            res = requests.get(
                url,
                auth=HTTPBasicAuth(
                    pipeline_.source.config[source.ObserviumSource.USERNAME],
                    pipeline_.source.config[source.ObserviumSource.PASSWORD],
                ),
                params=params,
                verify=pipeline_.source.verify_ssl,
                timeout=pipeline_.source.query_timeout,
            )
            res.raise_for_status()
            return res.json()[response_key]
        except requests.HTTPError as e:
            monitoring.metrics.SOURCE_HTTP_ERRORS.labels(pipeline_.name, pipeline_.source.type,
                                                         e.response.status_code).inc(1)
            logger_.error(str(e))
            if i == N_REQUESTS_TRIES:
                raise
            time.sleep(2**i)


def _add_devices_data(data: dict, pipeline_: Pipeline):
    SYS_NAME = 'sysName'
    LOCATION = 'location'
    devices = _get_devices(pipeline_)
    for obj in data.values():
        if SYS_NAME in obj:
            raise Exception(
                f'Data already contains the key `{SYS_NAME}` which was going to be added to it from devices'
            )
        if LOCATION in obj:
            raise Exception(
                f'Data already contains the key `{LOCATION}` which was going to be added to it from devices'
            )
        obj[SYS_NAME] = devices[obj['device_id']][SYS_NAME]
        obj[LOCATION] = devices[obj['device_id']][LOCATION]
    return data


def _get_devices(pipeline_: Pipeline):
    devices = _get(
        pipeline_,
        urllib.parse.urljoin(pipeline_.source.config[source.ObserviumSource.URL], '/api/v0/devices'),
        {},
        'devices',
    )
    return {obj['device_id']: obj for obj in devices.values()}


def _create_metrics(data: dict, pipeline_: Pipeline) -> list:
    metrics = []
    # these values must be outside the for loop for optimization purposes
    fields = field.build_fields(pipeline_.dimension_configurations)
    value_paths = pipeline_.value_paths
    value_paths = dict(zip(value_paths, value_paths))
    timestamp_key = POLL_TIME_KEYS[pipeline_.source.config['endpoint']]
    schema_id = pipeline_.get_schema_id()
    for obj in data.values():
        metric = {
            "timestamp": obj[timestamp_key],
            "dimensions": field.extract_fields(fields, obj),
            "measurements": {str(k): float(v) for k, v in obj.items() if str(k) in value_paths},
            "schemaId": schema_id,
        }
        metrics.append(metric)
    return metrics
