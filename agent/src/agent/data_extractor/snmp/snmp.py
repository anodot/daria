import time
from itertools import product, groupby
from urllib.parse import urlparse
from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi import CommunityData, ContextData, UdpTransportTarget, getCmd, nextCmd
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from agent.data_extractor.snmp.delta_calculator import DeltaCalculator
from agent.modules import logger
from agent.modules.constants import SNMP_DEFAULT_PORT
from agent.pipeline import Pipeline

logger_ = logger.get_logger(__name__, stdout=True)
delta_calculator = DeltaCalculator()

HOSTNAME_OID = '1.3.6.1.2.1.1.5.0'
HOSTNAME_NAME = 'host_name'
HOSTNAME_PATH = 'sysName'


def extract_metrics(pipeline_: Pipeline) -> list:
    metrics = []
    var_binds_group = _fetch_data(pipeline_)
    for var_binds in var_binds_group:
        if metric := _create_metric(pipeline_, var_binds):
            metrics.append(metric)
    if 'table_oids' in pipeline_.config:
        var_binds_group = _fetch_table_data(pipeline_)
        for var_binds in var_binds_group:
            if metric := _create_metric(pipeline_, var_binds):
                metrics.append(metric)
    return metrics


def fetch_raw_data(pipeline_: Pipeline) -> dict:
    data = {}
    var_binds_group = _fetch_raw_data(pipeline_)
    for var_binds in var_binds_group:
        for var_bind in var_binds:
            k = str(var_bind[0])
            v = str(var_bind[1])
            if k in data:
                raise SNMPError(f'`{k}` already exists')
            data[k] = v
    return data


def _get_var_binds(iterator, host):
    var_binds_groups = []
    for error_indication, error_status, error_index, var_binds in iterator:
        if error_indication:
            logger_.warning(f'{error_indication} for the {host}')
            continue
        elif error_status:
            message = f'{error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1][0] or "?"}'
            logger_.warning(f'{message} for the {host}')
            continue
        else:
            var_binds_groups.append(var_binds)
    return var_binds_groups


def _fetch_raw_data(pipeline_: Pipeline) -> list:
    snmp_version = 0 if pipeline_.source.version == 'v1' else 1
    var_binds_groups = []
    for host in pipeline_.source.hosts:
        host_ = host if '://' in host else f'//{host}'
        url = urlparse(host_)
        request_var_binds = [ObjectType(ObjectIdentity(oid)) for oid in pipeline_.config['oids']]
        iterator = _execute_cmd('get', pipeline_, snmp_version, url, request_var_binds)
        var_binds = _get_var_binds(iterator, host)
        var_binds_groups.extend(var_binds)
    return var_binds_groups


def _fetch_data(pipeline_: Pipeline) -> list:
    snmp_version = 0 if pipeline_.source.version == 'v1' else 1
    var_binds_groups = []
    for host in pipeline_.source.hosts:
        host_ = host if '://' in host else f'//{host}'
        url = urlparse(host_)

        request_var_binds = [ObjectType(ObjectIdentity(oid)) for oid in pipeline_.config['values_oids']]
        iterator = _execute_cmd('get', pipeline_, snmp_version, url, request_var_binds)
        values_var_binds = _get_var_binds(iterator, host)
        if not any(values_var_binds):
            continue

        request_var_binds = [ObjectType(ObjectIdentity(oid)) for oid in pipeline_.config['dimension_oids']]
        iterator = _execute_cmd('get', pipeline_, snmp_version, url, request_var_binds)
        if dimension_var_binds := _get_var_binds(iterator, host):
            var_binds_groups.extend(group + dimension_var_binds[0] for group in values_var_binds)
    return var_binds_groups


def _fetch_table_data(pipeline_: Pipeline) -> list:
    snmp_version = 0 if pipeline_.source.version == 'v1' else 1
    var_binds_groups = []
    for host in pipeline_.source.hosts:
        host_ = host if '://' in host else f'//{host}'
        url = urlparse(host_)

        request_var_binds = [ObjectType(ObjectIdentity(mib)) for mib in pipeline_.config['dimension_oids']]
        iterator = _execute_cmd('get', pipeline_, snmp_version, url, request_var_binds)
        dimension_var_binds = _get_var_binds(iterator, host)
        if not dimension_var_binds:
            continue

        for table_oid, mib, names, use_indexes in pipeline_.config['table_oids']:
            object_id_args = list(product([mib], names, use_indexes)) if use_indexes else list(product([mib], names))
            cmd_name = 'get' if use_indexes else 'next'
            request_var_binds = [ObjectType(ObjectIdentity(*args)) for args in object_id_args]
            iterator = _execute_cmd(cmd_name, pipeline_, snmp_version, url, request_var_binds)
            table_var_binds = _group_by_indexes(_get_var_binds(iterator, host)) if use_indexes else _get_var_binds(iterator, host)
            var_binds_groups.extend(group + dimension_var_binds[0] for group in table_var_binds)

    return var_binds_groups


def _group_by_indexes(table_var_binds):
    sorted_table = sorted(table_var_binds[0], key=lambda x: str(x[0])[-1])
    return [list(g) for k, g in groupby(sorted_table, key=lambda x: str(x[0])[-1])]


def _execute_cmd(name, pipeline_, snmp_version, url, var_binds):
    if name == 'get':
        cmd = getCmd
        lexicographic_mode = True
    elif name == 'next':
        cmd = nextCmd
        lexicographic_mode = False
    else:
        return []

    return cmd(
        SnmpEngine(),
        CommunityData(pipeline_.source.read_community, mpModel=snmp_version),
        UdpTransportTarget((url.hostname, url.port or SNMP_DEFAULT_PORT),
                           timeout=pipeline_.source.query_timeout,
                           retries=0),
        ContextData(),
        *var_binds,
        lookupMib=True,
        lookupNames=True,
        lexicographicMode=lexicographic_mode
    )


def _create_metric(pipeline_: Pipeline, var_binds: list) -> dict:
    metric = {
        'measurements': {},
        'schemaId': pipeline_.get_schema_id(),
        'dimensions': {},
        'tags': {},
    }

    for var_bind in var_binds:
        logger_.debug(f'Processing OID: {str(var_bind[0])}')
        if _is_value(var_bind[0], pipeline_):
            measurement_name = _get_measurement_name(var_bind[0], pipeline_)
            measurement_value = _get_value(var_bind, pipeline_)
            metric['measurements'][measurement_name] = measurement_value
            logger_.debug(f'Measurement `{measurement_name}` with a value: {measurement_value}')
        elif _is_dimension(var_bind[0], pipeline_):
            dimension_name = _get_dimension_name(var_bind[0], pipeline_)
            metric['dimensions'][dimension_name] = str(var_bind[1])
            logger_.debug(f'Dimension `{dimension_name}` with a value: {str(var_bind[1])}')
    if not metric['measurements'] or not metric['dimensions']:
        logger_.warning('No metrics extracted')
        return {}
    metric['timestamp'] = int(time.time())
    return metric


def _is_value(oid: ObjectIdentity, pipeline_: Pipeline) -> bool:
    return str(oid) in pipeline_.values or oid.getMibNode().label in pipeline_.values


def _is_dimension(oid: ObjectIdentity, pipeline_: Pipeline) -> bool:
    return str(oid) in pipeline_.dimension_paths or oid.getMibNode().label in pipeline_.dimension_paths


def _get_dimension_name(oid: ObjectIdentity, pipeline_: Pipeline) -> str:
    if str(oid) in pipeline_.dimension_paths_with_names:
        return pipeline_.dimension_paths_with_names[str(oid)]
    label = oid.getMibNode().label
    return pipeline_.dimension_paths_with_names.get(label, label)


def _get_measurement_name(oid: ObjectIdentity, pipeline_: Pipeline) -> str:
    if str(oid) in pipeline_.measurement_name_for_each_value:
        return pipeline_.measurement_name_for_each_value[str(oid)]
    label = oid.getMibNode().label
    return pipeline_.measurement_name_for_each_value.get(label, label)


def _get_value_oid_name(oid: ObjectIdentity, pipeline_: Pipeline) -> str:
    return str(oid) if str(oid) in pipeline_.values else oid.getMibNode().label


def _get_value(var_bind, pipeline_: Pipeline):
    if not str(var_bind[1]):
        return None
    if _is_running_counter(var_bind, pipeline_):
        value_name = _get_value_oid_name(var_bind[0], pipeline_)
        return delta_calculator.delta(value_name, float(var_bind[1]))
    return float(var_bind[1])


def _is_running_counter(var_bind, pipeline_) -> bool:
    value_name = _get_value_oid_name(var_bind[0], pipeline_)
    return pipeline_.values[value_name] == Pipeline.RUNNING_COUNTER


class SNMPError(Exception):
    pass
