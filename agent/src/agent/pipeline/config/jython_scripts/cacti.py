global sdc

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


def get_step():
    return int(sdc.userParams['STEP_IN_SECONDS'])


def get_now_with_delay():
    return int(time.time()) - int(sdc.userParams['DELAY_IN_MINUTES']) * 60


entityName = ''

if sdc.lastOffsets.containsKey(entityName):
    offset = int(float(sdc.lastOffsets.get(entityName)))
elif sdc.userParams['DAYS_TO_BACKFILL']:
    offset = to_timestamp(datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=int(sdc.userParams['DAYS_TO_BACKFILL'])))
else:
    offset = to_timestamp(datetime.utcnow().replace(second=0, microsecond=0))

sdc.log.info('OFFSET: ' + str(offset))

while True:
    if sdc.isStopped():
        break
    end = offset + get_interval()
    if end > get_now_with_delay():
        time.sleep(end - get_now_with_delay())

    batch = sdc.createBatch()

    res = requests.get(
        sdc.userParams['RRD_SOURCE_URL'],
        json={
            'start': offset,
            'end': offset + get_interval(),
            'step': get_step(),
        }
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
