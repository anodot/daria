import time

from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi import getCmd, CommunityData, UdpTransportTarget, ContextData
from pysnmp.smi.rfc1902 import ObjectType, ObjectIdentity
from agent.data_extractor.snmp.delta_calculator import DeltaCalculator
from agent.modules import logger
from agent.pipeline import Pipeline
from urllib.parse import urlparse

logger_ = logger.get_logger(__name__, stdout=True)
delta_calculator = DeltaCalculator()

HOSTNAME_OID = '1.3.6.1.2.1.1.5.0'


# todo do I need to rename oids to readable names?
def extract_metrics(pipeline_: Pipeline) -> list:
    metrics = []
    for response in _fetch_data(pipeline_):
        var_binds = _get_var_binds(response)
        metric = _create_metric(pipeline_, var_binds)
        metrics.append(metric)
    return metrics


def fetch_raw_data(pipeline_: Pipeline) -> dict:
    data = {}
    for response in _fetch_data(pipeline_):
        var_binds = _get_var_binds(response)
        for var_bind in var_binds:
            k = str(var_bind[0])
            v = str(var_bind[1])
            if k in data:
                raise Exception(f'`{k}` already exists')
            data[k] = v
    return data


def _get_var_binds(response):
    error_indication, error_status, error_index, var_binds = response
    if error_indication:
        logger_.error(error_indication)
        raise SNMPError(error_indication)
    elif error_status:
        message = '%s at %s' % (
            error_status.prettyPrint(),
            error_index and var_binds[int(error_index) - 1][0] or '?'
        )
        logger_.error(message)
        raise SNMPError(message)
    return var_binds


def _fetch_data(pipeline_: Pipeline):
    url = urlparse(pipeline_.source.url)
    return getCmd(
        SnmpEngine(),
        CommunityData(pipeline_.source.read_community, mpModel=0),
        UdpTransportTarget((url.hostname, url.port), timeout=pipeline_.source.query_timeout, retries=0),
        ContextData(),
        *[ObjectType(ObjectIdentity(mib)) for mib in pipeline_.config['oids']],
        lookupNames=True,
        lookupMib=True
    )


def _create_metric(pipeline_: Pipeline, var_binds: list) -> dict:
    metric = {
        'measurements': {},
        'schemaId': pipeline_.get_schema_id(),
        'dimensions': {},
        'tags': {},
    }

    for var_bind in var_binds:
        if _is_value(str(var_bind[0]), pipeline_):
            metric['measurements'][_get_measurement_name(var_bind[0], pipeline_)] = _get_value(var_bind, pipeline_)
        elif _is_dimension(str(var_bind[0]), pipeline_):
            metric['dimensions'][var_bind[0].getMibNode().label] = str(var_bind[1])
    metric['timestamp'] = int(time.time())
    return metric


def _is_value(key: str, pipeline_: Pipeline) -> bool:
    return key in pipeline_.values


def _is_dimension(key: str, pipeline_: Pipeline) -> bool:
    return key in pipeline_.all_dimensions


def _get_measurement_name(oid: ObjectIdentity, pipeline_: Pipeline) -> str:
    if str(oid) in pipeline_.measurement_names:
        # todo it can't work correctly, measurement_names is and array
        # todo потестить
        return pipeline_.measurement_names[str(oid)]
    return oid.getMibNode().label


def _get_value(var_bind, pipeline_: Pipeline):
    if _is_running_counter(var_bind, pipeline_):
        return delta_calculator.delta(str(var_bind[0]), float(var_bind[1]))
    return float(var_bind[1])


def _is_running_counter(var_bind, pipeline_) -> bool:
    return pipeline_.values[str(var_bind[0])] == Pipeline.RUNNING_COUNTER


class SNMPError(Exception):
    pass
