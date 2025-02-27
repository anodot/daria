global sdc

try:
    sdc.importLock()
    import time
    import os
    import sys
    import math
    from datetime import datetime, timedelta

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import pytz
    import requests
finally:
    sdc.importUnlock()


pipeline_timezone = pytz.timezone(sdc.userParams['TIMEZONE'])

def get_interval():
    return int(sdc.userParams['INTERVAL_IN_SECONDS'])


def disable_backfill():
    return bool(int(sdc.userParams['DISABLE_BACKFILL']))


def get_interval_missing_data():
    return int(sdc.userParams['QUERY_MISSING_DATA_INTERVAL'] or 0)


def get_now():
    if sdc.userParams['TIMEZONE'] != 'UTC':
        now = int(time.mktime(datetime.now(pipeline_timezone).timetuple()))
    else:
        now = int(time.time())
    return now


def get_now_with_delay():
    return get_now() - int(sdc.userParams['DELAY_IN_SECONDS'])


def to_timestamp(date):
    epoch = datetime(1970, 1, 1).replace(tzinfo=pytz.UTC)
    return int((date - epoch).total_seconds())


def query_missing_data(main_offset, main_interval):
    now = get_now()
    sdc.log.info('Start query_missing_data at: {}'.format(str(datetime.fromtimestamp(now))))
    db_offset = get_db_offset()
    if not db_offset:
        return now

    # compute start timestamp of the bucket where the latest db_offset is
    start = main_offset - main_interval * math.ceil((main_offset - db_offset) / main_interval)

    # search missing data points by buckets
    while start < main_offset - main_interval and not sdc.isStopped():
        sdc.log.info('Processing missed data: from {} to {}'.format(str(datetime.fromtimestamp(start)), str(datetime.fromtimestamp(start + main_interval))))
        cur_batch = sdc.createBatch()
        record = sdc.createRecord('record created ' + str(datetime.now()))
        record.value = {'last_timestamp': int(start)}
        record.value = {'last_timestamp_iso': datetime.fromtimestamp(int(start)).isoformat()}
        cur_batch.add(record)
        cur_batch.process(entityName, str(start))
        start += main_interval

    return now


def get_db_offset():
    try:
        res = requests.get(sdc.userParams['PIPELINE_OFFSET_ENDPOINT'])
        res.raise_for_status()
        data = res.json()
        if not data or type(data) == str:
            raise ValueError('No offset found in DB')
        return int(float(data['timestamp']))
    except (requests.ConnectionError, requests.HTTPError, ValueError) as e:
        sdc.log.error(str(e))
        return None


entityName = ''


def main():
    interval = timedelta(seconds=get_interval())
    missing_data_last_ts = 0
    missing_data_interval = get_interval_missing_data()

    if sdc.lastOffsets.containsKey(entityName):
        offset = int(float(sdc.lastOffsets.get(entityName)))
    elif sdc.userParams['INITIAL_OFFSET']:
        offset = int(float(sdc.userParams['INITIAL_OFFSET']))
    else:
        offset = get_now() - get_interval()

    sdc.log.info('OFFSET: ' + str(offset))

    while True:
        if sdc.isStopped():
            break

        while offset > get_now_with_delay() - interval.total_seconds():
            if missing_data_interval and get_now() > missing_data_last_ts + missing_data_interval and not sdc.isPreview():
                missing_data_last_ts = query_missing_data(int(offset), interval.total_seconds())

            time.sleep(2)
            if sdc.isStopped():
                return

        cur_batch = sdc.createBatch()
        record = sdc.createRecord('record created ' + str(datetime.now()))
        sdc.log.debug('last_timestamp: {}-{}'.format(str(datetime.fromtimestamp(int(offset))), str(offset)))
        val = int(offset)
        record.value = {
            'last_timestamp': val,
            'last_timestamp_iso': datetime.fromtimestamp(val).isoformat()
        }

        offset += interval.total_seconds()
        cur_batch.add(record)
        cur_batch.process(entityName, str(offset))


def main_no_backfill():
    interval_seconds = get_interval()
    while True:
        if sdc.isStopped():
            break
        current_time = get_now()

        # Calculate the next execution time aligned to the interval
        next_execution_time = (current_time // interval_seconds + 1) * interval_seconds

        # if preview - send query instantly
        if not sdc.isPreview():
            time.sleep(next_execution_time - current_time)

        sdc.log.info("Executing query at: " + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()))
        cur_batch = sdc.createBatch()
        record = sdc.createRecord('record created ' + str(datetime.now()))
        val = next_execution_time - interval_seconds  # we need to send last queried timestamp
        record.value = {
            'last_timestamp': val,
            'last_timestamp_iso': datetime.fromtimestamp(val).isoformat()
        }
        cur_batch.add(record)
        cur_batch.process(entityName, str(get_now()))


if disable_backfill():
    main_no_backfill()
else:
    main()
