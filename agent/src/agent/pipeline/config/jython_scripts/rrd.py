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


def get_now_with_delay():
    return int(time.time()) - int(sdc.userParams['DELAY_IN_MINUTES']) * 60


def get_step():
    return int(sdc.userParams['STEP_IN_SECONDS'])


entityName = ''


def main():
    if sdc.lastOffsets.containsKey(entityName):
        offset = int(float(sdc.lastOffsets.get(entityName)))
    elif sdc.userParams['DAYS_TO_BACKFILL']:
        offset = to_timestamp(
            datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            - timedelta(days=int(sdc.userParams['DAYS_TO_BACKFILL']))
        )
    else:
        # todo should it run on a specific time? Like on 5 mins, or 10 mins, I mean 05, 10, 15, 20 mins etc.
        offset = to_timestamp(datetime.utcnow().replace(second=0, microsecond=0))

    sdc.log.info('OFFSET: ' + str(offset))

    tries = 0
    while True:
        if sdc.isStopped():
            break
        end = offset + get_interval()
        while end > get_now_with_delay():
            time.sleep(2)
            if sdc.isStopped():
                return

        batch = sdc.createBatch()

        res = requests.get(
            sdc.userParams['RRD_SOURCE_URL'],
            params={
                'start': offset,
                'end': offset + get_interval(),
                'step': get_step(),
            }
        )
        if res.status_code == 204:
            # this means the rrd archive has been removed by the script that copies it via scp
            # and we should wait until a new version of the file is uploaded and try again
            tries += 1
            if tries == MAX_TRIES:
                raise Exception(
                    'extract_metrics endpoint returned 204 status code %s times in a row. The archive with rrd files does not exist'
                    % MAX_TRIES
                )
            time.sleep(30)
            continue
        tries = 0
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


main()
