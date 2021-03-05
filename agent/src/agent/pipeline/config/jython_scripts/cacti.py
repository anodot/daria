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


entityName = ''

if sdc.lastOffsets.containsKey(entityName):
    offset = int(float(sdc.lastOffsets.get(entityName)))
# it will be implemented a bit later
# elif sdc.userParams['INITIAL_OFFSET']:
#     offset = to_timestamp(datetime.strptime(sdc.userParams['INITIAL_OFFSET'], '%d/%m/%Y %H:%M'))
else:
    offset = to_timestamp(datetime.utcnow().replace(second=0, microsecond=0) - timedelta(seconds=get_interval()))

sdc.log.info('OFFSET: ' + str(offset))

while True:
    if sdc.isStopped():
        break
    now = int(time.time())
    if offset < now + get_interval():
        time.sleep(now + get_interval() - offset)

    batch = sdc.createBatch()

    metrics = requests.post(
        sdc.userParams['RRD_SOURCE_URL'],
        json={
            'start': offset,
            'end': offset + get_interval(),
            'step': get_interval(),
        }
    )
    for metric in metrics:
        record = sdc.createRecord('record created ' + str(datetime.now()))
        record.value = metric
        batch.add(record)

    offset += get_interval()
    batch.process(entityName, str(offset))
