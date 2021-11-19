global sdc

try:
    sdc.importLock()
    import sys
    import os
    import time
    import traceback
    import re

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests

    from datetime import datetime, timedelta
    from requests.auth import HTTPBasicAuth
finally:
    sdc.importUnlock()

# single threaded - no entityName because we need only one offset
entityName = ''
LAST_TIMESTAMP = '%last_timestamp%'
N_REQUESTS_TRIES = 3


POLL_TIME_KEYS = {
    'ports': 'poll_time',
    'mempools': 'mempool_polled',
    'processors': 'processor_polled',
    'storage': 'storage_polled'
}

RESPONSE_DATA_KEYS = {
    'ports': 'ports',
    'mempools': 'entries',
    'processors': 'entries',
    'storage': 'storage'
}


def _replace_illegal_chars(value):
    value = value.strip().replace(".", "_")
    return re.sub('\s+', '_', value)


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


def _add_default_dimensions(data):
    devices = get_devices()
    for obj in data.values():
        if 'sysName' in obj:
            raise Exception('Data already contains the key `sysName` which should have been added to it from devices')
        if 'location' in obj:
            raise Exception('Data already contains the key `location` which should have been added to it from devices')
        obj['sysName'] = devices[obj['device_id']]['sysName']
        obj['location'] = devices[obj['device_id']]['location']
    return data


def get_devices():
    devices = _get(
        sdc.userParams['DEVICES_URL'],
        {},
        'devices'
    )
    return {obj['device_id']: obj for obj in devices.values()}


def create_metrics(data):
    metrics = []
    for obj in data.values():
        metric = {
            "timestamp": obj[POLL_TIME_KEYS[sdc.userParams['ENDPOINT']]],
            "dimensions": {
                sdc.userParams['DIMENSIONS'][k]: _replace_illegal_chars(v)
                for k, v in obj.items() if k in sdc.userParams['DIMENSIONS']
            },
            "measurements": {
                _replace_illegal_chars(k): float(v) for k, v in obj.items() if k in sdc.userParams['MEASUREMENTS']
            },
            "schemaId": sdc.userParams['SCHEMA_ID'],
        }
        metrics.append(metric)
    return metrics


def main():
    if sdc.lastOffsets.containsKey(entityName):
        offset = int(float(sdc.lastOffsets.get(entityName)))
    else:
        offset = to_timestamp(datetime.now().replace(second=0, microsecond=0))

    sdc.log.info('Start offset: ' + str(offset))

    cur_batch = sdc.createBatch()

    while True:
        try:
            while offset > get_now_with_delay():
                time.sleep(2)
                if sdc.isStopped():
                    return cur_batch, offset

            data = _get(
                sdc.userParams['URL'],
                sdc.userParams['REQUEST_PARAMS'],
                RESPONSE_DATA_KEYS[sdc.userParams['ENDPOINT']]
            )
            data = _add_default_dimensions(data)

            for metric in create_metrics(data):
                record = sdc.createRecord('record created ' + str(datetime.now()))
                record.value = metric
                cur_batch.add(record)

                if cur_batch.size() == sdc.batchSize:
                    cur_batch.process(entityName, str(offset + get_interval()))
                    cur_batch = sdc.createBatch()

            cur_batch.process(entityName, str(offset + get_interval()))
            cur_batch = sdc.createBatch()
            offset += get_interval()
        except Exception:
            sdc.log.error(traceback.format_exc())
            raise


batch, offset_ = main()
if batch.size() + batch.errorCount() + batch.eventCount() > 0:
    batch.process(entityName, str(offset_ + get_interval()))
