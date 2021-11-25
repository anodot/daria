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

entityName = ''


def to_timestamp(date):
    epoch = datetime(1970, 1, 1)
    return int((date - epoch).total_seconds())


def get_interval():
    return int(sdc.userParams['INTERVAL_IN_SECONDS'])


def get_now():
    return int(time.time())


def main():
    if sdc.lastOffsets.containsKey(entityName):
        offset = int(float(sdc.lastOffsets.get(entityName)))
    else:
        offset = to_timestamp(datetime.now())

    sdc.log.info('OFFSET: ' + str(offset))

    while True:
        now = get_now()
        if sdc.isStopped():
            return
        while offset > get_now():
            time.sleep(2)
            if sdc.isStopped():
                return
        offset = now + get_interval()

        batch = sdc.createBatch()

        res = requests.get(sdc.userParams['SNMP_SOURCE_URL'], timeout=60)
        res.raise_for_status()
        for metric in res.json():
            metric['timestamp'] = now
            record = sdc.createRecord('record created ' + str(datetime.now()))
            record.value = metric
            batch.add(record)

            if batch.size() == sdc.batchSize:
                batch.process(entityName, str(offset))
                batch = sdc.createBatch()

        event = sdc.createEvent('interval_processed', 1)
        event.value = {
            'watermark': now,
            'schemaId': sdc.userParams['SCHEMA_ID']
        }
        batch.addEvent(event)
        batch.process(entityName, str(offset))


main()
