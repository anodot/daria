global sdc

MAX_TRIES = 3

try:
    sdc.importLock()
    import sys
    import os
    import time
    from datetime import datetime, timedelta

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
finally:
    sdc.importUnlock()


def to_timestamp(date):
    epoch = datetime(1970, 1, 1)
    return int((date - epoch).total_seconds())


def get_interval():
    return int(sdc.userParams['INTERVAL_IN_SECONDS'])


def get_now():
    return int(time.time())


def get_step():
    return int(sdc.userParams['STEP_IN_SECONDS'])


entityName = ''

if sdc.lastOffsets.containsKey(entityName):
    offset = int(float(sdc.lastOffsets.get(entityName)))
else:
    offset = to_timestamp(datetime.now().replace(second=0, microsecond=0))

sdc.log.info('OFFSET: ' + str(offset))

while True:
    if sdc.isStopped():
        break
    end = offset + get_interval()
    if end > get_now():
        time.sleep(end - get_now())

    batch = sdc.createBatch()

    res = requests.get(
        sdc.userParams['SNMP_SOURCE_URL'],
        params={}
    )
    res.raise_for_status()
    for metric in res.json():
        record = sdc.createRecord('record created ' + str(datetime.now()))
        record.value = metric
        batch.add(record)

        if batch.size() == sdc.batchSize:
            batch.process(entityName, str(end))
            batch = sdc.createBatch()
            if sdc.isStopped():
                break

    offset += get_interval()
    batch.process(entityName, str(offset))
