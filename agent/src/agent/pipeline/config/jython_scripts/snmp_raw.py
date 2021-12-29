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


entityName = ''

if sdc.lastOffsets.containsKey(entityName):
    offset = int(float(sdc.lastOffsets.get(entityName)))
else:
    offset = to_timestamp(datetime.now().replace(second=0, microsecond=0))

while True:
    if sdc.isStopped():
        break
    if offset > get_now():
        time.sleep(offset - get_now())

    batch = sdc.createBatch()

    res = requests.get(sdc.userParams['SNMP_SOURCE_URL'], timeout=60)
    res.raise_for_status()
    record = sdc.createRecord('record created ' + str(datetime.now()))
    record.value = sdc.createMap(True)
    for k, v in res.json().items():
        record.value[k] = v
    batch.add(record)

    batch.process(entityName, str(offset))
    offset += get_interval()