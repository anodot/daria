import time
import requests
import urllib.parse

from requests.auth import HTTPBasicAuth
from agent import source
from agent.data_extractor.topology import topology, lookup
from agent.modules import logger, tools
from agent.pipeline import Pipeline
from agent.source import ObserviumSource

logger_ = logger.get_logger(__name__)

N_REQUESTS_TRIES = 3

POLL_TIME_KEYS = {
    'ports': 'poll_time',
    'mempools': 'mempool_polled',
    'processors': 'processor_polled',
    'storage': 'storage_polled'
}

RESPONSE_DATA_KEYS = {'ports': 'ports', 'mempools': 'entries', 'processors': 'entries', 'storage': 'storage'}


# todo schema definition
# todo make sure all dimensions have configuration
def extract_metrics(pipeline_: Pipeline) -> list:
    # todo can we init lookup somewhere always? or keep it explicit
    lookup.init_sources(pipeline_.config.get('lookup', {}))
    # todo
    base_url = urllib.parse.urljoin(pipeline_.source.config[source.ObserviumSource.URL], '/api/v0/')
    endpoint = pipeline_.source.config['endpoint']
    data = _get(
        pipeline_.source,
        # todo
        # urllib.parse.urljoin(base_url, endpoint),
        'http://localhost:8080/api/v0/ports',
        pipeline_.config.get('request_params', {}),
        RESPONSE_DATA_KEYS[endpoint]
    )
    data = _add_devices_data(data, pipeline_)
    return _create_metrics(data, endpoint, pipeline_)


def _get(source_: ObserviumSource, url, params, response_key):
    for i in range(1, N_REQUESTS_TRIES + 1):
        try:
            res = requests.get(
                url,
                # todo keys
                auth=HTTPBasicAuth(
                    source_.config[source.ObserviumSource.USERNAME], source_.config[source.ObserviumSource.PASSWORD]
                ),
                params=params,
                verify=source_.verify_ssl,
                timeout=source_.query_timeout,
            )
            res.raise_for_status()
            return res.json()[response_key]
        except requests.HTTPError as e:
            # todo
            # requests.post(sdc.userParams['MONITORING_URL'] + str(res.status_code))
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
                f'Data already contains the key `{SYS_NAME}` which should have been added to it from devices'
            )
        if LOCATION in obj:
            raise Exception(
                f'Data already contains the key `{LOCATION}` which should have been added to it from devices'
            )
        obj[SYS_NAME] = devices[obj['device_id']]['sysName']
        obj[LOCATION] = devices[obj['device_id']]['location']
    return data


def _get_devices(pipeline_: Pipeline):
    devices = _get(
        pipeline_.source,
        # urllib.parse.urljoin(pipeline_.source.config[source.ObserviumSource.URL], '/api/v0/devices'),
        # todo it's temporary
        'http://localhost:8080/api/v0/devices',
        {},
        'devices'
    )
    return {obj['device_id']: obj for obj in devices.values()}


# todo it might be a class. Will keep endpoint and pipeline and no need to pass it everywhere
def _create_metrics(data: dict, endpoint: str, pipeline_: Pipeline) -> list:
    # todo replace illegal chars in one place, don't forget
    # todo dimensions have name inside, but for lookup name is a key in configuration. Is it ok?
    metrics = []
    dimensions = topology.field.build_fields(pipeline_.new_dimensions)
    for obj in data.values():
        metric = {
            # todo why do I need endpoint here?
            "timestamp": obj[POLL_TIME_KEYS[endpoint]],
            # todo check do I need these checks in dims and is not None
            # "dimensions": {
            #     dimensions[k]: tools.replace_illegal_chars(v)
            #     for k, v in obj.items() if k in dimensions and v is not None
            # },
            "dimensions": topology.extract_fields(dimensions, obj),
            "measurements": {
                tools.replace_illegal_chars(k): float(v)
                for k, v in obj.items() if k in list(pipeline_.value_paths)
            },
            "schemaId": pipeline_.get_schema_id(),
        }
        metrics.append(metric)
    return metrics
