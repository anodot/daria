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


def get_now():
    return int(time.time())


def get_next_offset():
    dt = datetime.utcnow().replace(second=0, microsecond=0)
    if sdc.userParams['BUCKET_SIZE'] == '5m':
        dt = dt + timedelta(minutes=5 - dt.minute % 5)
    elif sdc.userParams['BUCKET_SIZE'] == '1h':
        dt = dt.replace(minute=0) + timedelta(hours=1)
    else:
        dt = dt + timedelta(seconds=get_interval())
    return to_timestamp(dt)


def get_offset_with_delay(offset):
    return offset + int(sdc.userParams['DELAY_IN_MINUTES']) * 60


def to_timestamp(date):
    epoch = datetime(1970, 1, 1)
    return int((date - epoch).total_seconds())


def get_interval():
    return int(sdc.userParams['INTERVAL_IN_SECONDS'])


def main():
    if sdc.lastOffsets.containsKey(entityName):
        offset = int(float(sdc.lastOffsets.get(entityName)))
    else:
        offset = to_timestamp(datetime.utcnow().replace(minute=0, second=0, microsecond=0))

    sdc.log.info('Start offset: ' + str(offset))

    batch = sdc.createBatch()

    while True:
        try:
            while get_offset_with_delay(offset) > get_now():
                time.sleep(2)
                if sdc.isStopped():
                    return batch, offset
            offset = get_next_offset()
            try:
                res = requests.get(sdc.userParams['AGENT_DATA_EXTRACTOR_URL'])
                res.raise_for_status()
            except requests.HTTPError as e:
                requests.post(sdc.userParams['MONITORING_URL'] + str(e.response.status_code))
                sdc.log.error(str(e))
                raise
            for metric in res.json():
                record = sdc.createRecord('record created ' + str(datetime.now()))
                record.value = metric
                '%TRANSFORM_SCRIPT_PLACEHOLDER%'

                batch.add(record)

                if batch.size() == sdc.batchSize:
                    batch.process(entityName, str(offset))
                    batch = sdc.createBatch()
                    if sdc.isStopped():
                        break

            event = sdc.createEvent('interval processed', 1)
            event.value = {
                'watermark': offset + get_interval(),
            }
            batch.addEvent(event)
            batch.process(entityName, str(offset))
            batch = sdc.createBatch()
        except Exception:
            sdc.log.error(traceback.format_exc())
            raise


batch_, offset_ = main()
if batch_.size() + batch_.errorCount() + batch_.eventCount() > 0:
    batch_.process(entityName, str(offset_ + get_interval()))
