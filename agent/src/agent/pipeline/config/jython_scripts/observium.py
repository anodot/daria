global sdc

try:
    sdc.importLock()
    import sys
    import os
    import time
    import traceback

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests

    from datetime import datetime, timedelta
    from requests.auth import HTTPBasicAuth
finally:
    sdc.importUnlock()

# single threaded - no entityName because we need only one offset
entityName = ''
LAST_TIMESTAMP = '%last_timestamp%'


def get_now_with_delay():
    return int(time.time()) - int(sdc.userParams['DELAY_IN_SECONDS'])


def to_timestamp(date):
    epoch = datetime(1970, 1, 1)
    return int((date - epoch).total_seconds())


def get_interval():
    return int(sdc.userParams['INTERVAL_IN_SECONDS'])


def _get(url, params, response_key):
    for i in range(1, N_REQUESTS_TRIES + 1):
        try:
            res = requests.get(
                url,
                auth=HTTPBasicAuth(sdc.userParams['API_USER'], sdc.userParams['API_PASSWORD']),
                params=params,
                verify=bool(sdc.userParams['VERIFY_SSL']),
                timeout=sdc.userParams['QUERY_TIMEOUT'],
            )
            res.raise_for_status()
            return res.json()[response_key]
        except requests.HTTPError as e:
            requests.post(sdc.userParams['MONITORING_URL'] + str(res.status_code))
            sdc.log.error(str(e))
            if i == N_REQUESTS_TRIES:
                raise
            time.sleep(2 ** i)


def get_ports():
    return _get(
        sdc.userParams['PORTS_URL'],
        sdc.userParams['PORTS_PARAMS'],
        'ports'
    )


def _transform(dict_, key):
    return {obj[key]: obj for obj in dict_.values()}


def get_devices():
    devices = _get(
        sdc.userParams['DEVICES_URL'],
        {},
        'devices'
    )
    return _transform(devices, 'device_id')


def get_mempools():
    mempools = _get(
        sdc.userParams['MEMPOOLS_URL'],
        sdc.userParams['MEMPOOLS_PARAMS'],
        'entries'
    )
    return _transform(mempools, 'mempool_id')


def get_processors():
    processors = _get(
        sdc.userParams['PROCESSORS_URL'],
        sdc.userParams['PROCESSOR_PARAMS'],
        'entries'
    )
    return _transform(processors, 'processor_id')


def get_storage():
    return _get(
        sdc.userParams['STORAGE_URL'],
        sdc.userParams['STORAGE_PARAMS'],
        'storage'
    )


def add_sys_name_and_location(metrics_, devices):
    for obj in metrics_:
        obj['dimensions']['sysName'] = devices[obj['device_id']]['sysName']
        obj['dimensions']['location'] = devices[obj['device_id']]['location']
    return metrics_


def create_metrics(data_, poll_time_key, dimensions, measurements):
    return [transform(obj, poll_time_key, dimensions, measurements) for obj in data_.values()]


def transform(data_, poll_time_key, dimensions, measurements):
    return {
        "timestamp": data_[poll_time_key],
        "dimensions": {k: v for k, v in data_.items() if k in dimensions},
        "measurements": {k: float(v) for k, v in data_.items() if k in measurements},
        "schemaId": sdc.userParams['SCHEMA_ID'],
    }


if sdc.lastOffsets.containsKey(entityName):
    offset = int(float(sdc.lastOffsets.get(entityName)))
elif sdc.userParams['DAYS_TO_BACKFILL']:
    offset = to_timestamp(datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=int(sdc.userParams['DAYS_TO_BACKFILL'])))
else:
    offset = to_timestamp(datetime.now().replace(second=0, microsecond=0))

sdc.log.info('Start offset: ' + str(offset))

cur_batch = sdc.createBatch()

N_REQUESTS_TRIES = 3

while True:
    try:
        end = offset + get_interval()
        if end > get_now_with_delay():
            time.sleep(end - get_now_with_delay())

        metrics = []
        devices_data = get_devices()
        ports_metrics = create_metrics(get_ports(), 'poll_time', sdc.userParams['PORTS_DIMENSIONS'], sdc.userParams['PORTS_MEASUREMENTS'])
        ports_metrics = add_sys_name_and_location(ports_metrics, devices_data)
        metrics.append(ports_metrics)

        mempools_metrics = create_metrics(get_mempools(), 'mempool_polled', sdc.userParams['MEMPOOLS_DIMENSIONS'], sdc.userParams['MEMPOOLS_MEASUREMENTS'])
        mempools_metrics = add_sys_name_and_location(mempools_metrics, devices_data)
        metrics.append(mempools_metrics)

        processors_metrics = create_metrics(get_processors(), 'processor_polled', sdc.userParams['PROCESSORS_DIMENSIONS'], sdc.userParams['PROCESSORS_MEASUREMENTS'])
        processors_metrics = add_sys_name_and_location(processors_metrics, devices_data)
        metrics.append(processors_metrics)

        storage_metrics = create_metrics(get_storage(), 'storage_polled', sdc.userParams['STORAGE_DIMENSIONS'], sdc.userParams['STORAGE_MEASUREMENTS'])
        storage_metrics = add_sys_name_and_location(storage_metrics, devices_data)
        metrics.append(storage_metrics)

        for metric in metrics:
            record = sdc.createRecord('record created ' + str(datetime.now()))
            record.value = metric
            cur_batch.add(record)

            if cur_batch.size() == sdc.batchSize:
                cur_batch.process(entityName, str(offset))
                cur_batch = sdc.createBatch()

        offset = end
        cur_batch.process(entityName, str(offset))
        cur_batch = sdc.createBatch()
        if sdc.isStopped():
            break
    except Exception as e:
        sdc.log.error(traceback.format_exc())
        raise

if cur_batch.size() + cur_batch.errorCount() + cur_batch.eventCount() > 0:
    cur_batch.process(entityName, str(offset))

# todo run it locally to debug