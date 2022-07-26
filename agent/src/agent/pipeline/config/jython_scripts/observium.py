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


def to_timestamp(date):
    epoch = datetime(1970, 1, 1)
    return int((date - epoch).total_seconds())


def round_timestamp(timestamp, round_to):
    return timestamp - (timestamp % round_to)


def wait_to_timestamp(timestamp):
    while get_now() < timestamp:
        time.sleep(1)


def get_delay():
    return int(sdc.userParams['DELAY_IN_SECONDS'])


def get_interval():
    return int(sdc.userParams['INTERVAL_IN_SECONDS'])


def get_observium_step():
    return int(sdc.userParams['OBSERVIUM_STEP_IN_SECONDS'])


def get_now():
    return int(time.time())


def main():
    if sdc.lastOffsets.containsKey(entityName):
        offset = int(float(sdc.lastOffsets.get(entityName)))
    else:
        offset = to_timestamp(datetime.utcnow().replace(minute=0, second=0, microsecond=0))

    sdc.log.info('Start offset: ' + str(offset))

    while True:
        try:
            batch = sdc.createBatch()
            while offset > get_now():
                time.sleep(1)
                if sdc.isStopped():
                    return batch, offset
            # we can get data for not earlier then observium step size, usually it's 5 minutes
            # if we already passed that time, we try to get the latest available data
            # which is from `now - observium step` to `now - observium step + interval`
            if offset - get_interval() < round_timestamp(get_now(), get_interval()) - get_observium_step():
                offset = round_timestamp(get_now(), get_interval()) - get_observium_step() + get_interval()
            wait_to_timestamp(offset + get_delay())
            try:
                res = requests.get(sdc.userParams['AGENT_DATA_EXTRACTOR_URL'], params={'offset': offset})
                res.raise_for_status()
            except requests.HTTPError as e:
                requests.post(sdc.userParams['MONITORING_URL'] + str(e.response.status_code))
                sdc.log.error(str(e))
                raise
            for metric in res.json():
                record = sdc.createRecord('record created ' + str(datetime.now()))
                record.value = metric
                batch.add(record)

                if batch.size() == sdc.batchSize:
                    batch.process(entityName, str(offset))
                    batch = sdc.createBatch()
                    if sdc.isStopped():
                        break
            event = sdc.createEvent('interval processed', 1)
            event.value = {
                'watermark': offset,
            }
            batch.addEvent(event)
            batch.process(entityName, str(offset))
            offset += get_interval()
        except Exception:
            sdc.log.error(traceback.format_exc())
            raise


batch_, offset_ = main()
if batch_.size() + batch_.errorCount() + batch_.eventCount() > 0:
    batch_.process(entityName, str(offset_ + get_interval()))
