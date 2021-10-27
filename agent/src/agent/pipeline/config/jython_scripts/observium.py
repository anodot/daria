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


POLL_TIME_KEYS = {
    'ports': 'poll_time',
    'mempools': 'mempool_polled',
    'processors': 'processor_polled',
    'storage': 'storage_polled'
}

DATA_KEYS = {
    'ports': 'ports',
    'mempools': 'entries',
    'processors': 'entries',
    'storage': 'storage'
}


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


def get_data():
    return _get(
        sdc.userParams['URL'],
        sdc.userParams['PARAMS'],
        DATA_KEYS[sdc.userParams['ENDPOINT']]
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


def add_sys_name_and_location(data):
    devices = get_devices()
    for obj in data.values():
        obj['sysName'] = devices[obj['device_id']]['sysName']
        obj['location'] = devices[obj['device_id']]['location']
    return data


def create_metrics(data_):
    return [transform(datum) for datum in data_.values()]


def transform(datum):
    metric = {
        "timestamp": datum[POLL_TIME_KEYS[sdc.userParams['ENDPOINT']]],
        "dimensions": {k: v for k, v in datum.items() if k in sdc.userParams['DIMENSIONS']},
        "measurements": {k: float(v) for k, v in datum.items() if k in sdc.userParams['MEASUREMENTS']},
        "schemaId": sdc.userParams['SCHEMA_ID'],
    }
    metric['dimensions']['sysName'] = datum['sysName']
    metric['dimensions']['location'] = datum['location']
    return metric


if sdc.lastOffsets.containsKey(entityName):
    offset = int(float(sdc.lastOffsets.get(entityName)))
elif sdc.userParams['DAYS_TO_BACKFILL'] and int(sdc.userParams['DAYS_TO_BACKFILL']) > 0:
    offset = to_timestamp(datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=int(sdc.userParams['DAYS_TO_BACKFILL'])))
else:
    offset = to_timestamp(datetime.now().replace(second=0, microsecond=0))

sdc.log.info('Start offset: ' + str(offset))

cur_batch = sdc.createBatch()

N_REQUESTS_TRIES = 3

while True:
    try:
        if sdc.isStopped():
            break
        while offset > get_now_with_delay():
            time.sleep(2)
            if sdc.isStopped():
                exit()

        data = add_sys_name_and_location(get_data())
        metrics = create_metrics(data)

        for metric in metrics:
            record = sdc.createRecord('record created ' + str(datetime.now()))
            record.value = metric
            cur_batch.add(record)

            if cur_batch.size() == sdc.batchSize:
                cur_batch.process(entityName, str(offset + get_interval()))
                cur_batch = sdc.createBatch()

        cur_batch.process(entityName, str(offset + get_interval()))
        cur_batch = sdc.createBatch()
        offset += get_interval()
    except Exception as e:
        sdc.log.error(traceback.format_exc())
        raise

if cur_batch.size() + cur_batch.errorCount() + cur_batch.eventCount() > 0:
    cur_batch.process(entityName, str(offset + get_interval()))
