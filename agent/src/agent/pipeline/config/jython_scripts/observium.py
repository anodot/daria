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


def get_ports():
    for i in range(1, N_REQUESTS_TRIES + 1):
        try:
            res = requests.get(
                sdc.userParams['PORTS_URL'],
                auth=HTTPBasicAuth(sdc.userParams['API_USER'], sdc.userParams['API_PASSWORD']),
                params=sdc.userParams['PORTS_PARAMS'],
                verify=bool(sdc.userParams['VERIFY_SSL']),
                timeout=sdc.userParams['QUERY_TIMEOUT'],
            )
            res.raise_for_status()
            return res.json()['ports']
        except requests.HTTPError as e:
            requests.post(sdc.userParams['MONITORING_URL'] + str(res.status_code))
            sdc.log.error(str(e))
            if i == N_REQUESTS_TRIES:
                raise
            time.sleep(2 ** i)


def get_devices():
    for i in range(1, N_REQUESTS_TRIES + 1):
        try:
            res = requests.get(
                sdc.userParams['DEVICES_URL'],
                auth=HTTPBasicAuth(sdc.userParams['API_USER'], sdc.userParams['API_PASSWORD']),
                # todo add or remove
                # params=params,
                verify=bool(sdc.userParams['VERIFY_SSL']),
                timeout=sdc.userParams['QUERY_TIMEOUT'],
            )
            res.raise_for_status()
            res = res.json()['devices']
            break
        except requests.HTTPError as e:
            requests.post(sdc.userParams['MONITORING_URL'] + str(res.status_code))
            sdc.log.error(str(e))
            if i == N_REQUESTS_TRIES:
                raise
            time.sleep(2 ** i)
    return {device['device_id']: device for device in res.values()}


def add_sys_name_and_location(ports_data, devices):
    for port in ports_data.values():
        # todo probably log or kind of if there's no such device?
        if port['device_id'] in devices:
            port['sysName'] = devices[port['device_id']]['sysName']
            port['location'] = devices[port['device_id']]['location']
    return ports_data


def create_metrics(ports_data):
    return [transform_port(port_data, sdc.userParams['DIMENSIONS'], sdc.userParams['MEASUREMENTS']) for port_data in ports_data.values()]


def transform_port(port_data, dimensions, measurements):
    return {
        "timestamp": port_data['poll_time'],
        "dimensions": {k: v for k, v in port_data.items() if k in dimensions},
        "measurements": {k: float(v) for k, v in port_data.items() if k in measurements},
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

        data = add_sys_name_and_location(get_ports(), get_devices())
        metrics = create_metrics(data)

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


# BIG TODO how to be with intervals?