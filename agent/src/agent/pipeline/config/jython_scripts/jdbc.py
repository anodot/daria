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


def get_interval():
    return int(sdc.userParams['INTERVAL_IN_SECONDS'])


def get_interval_missing_data():
    return int(sdc.userParams['QUERY_MISSING_DATA_INTERVAL'])


def get_now_with_delay():
    if sdc.userParams['WATERMARK_IN_LOCAL_TIMEZONE'] == 'True':
        now = int(time.mktime(datetime.now(pytz.timezone(sdc.userParams['TIMEZONE'])).timetuple()))
    else:
        now = int(time.time())
    return now - int(sdc.userParams['DELAY_IN_SECONDS'])


def to_timestamp(date):
    epoch = datetime(1970, 1, 1)
    return int((date - epoch).total_seconds())


def query_missing_data(main_offset, main_interval):
    db_offset = get_db_offset()
    if not db_offset:
        return

    # compute start timestamp of the bucket where the latest db_offset is
    start = main_offset - main_interval * math.ceil((main_offset - db_offset) / main_interval)

    # search missing data points by buckets
    while start < main_offset - main_interval:
        sdc.log.info('Processing missed data: from {} to {}'.format(str(datetime.fromtimestamp(start)), str(datetime.fromtimestamp(start + main_interval))))
        cur_batch = sdc.createBatch()
        record = sdc.createRecord('record created ' + str(datetime.now()))
        record.value = {'last_timestamp': int(start)}
        cur_batch.add(record)
        cur_batch.process(entityName, str(start))
        start += main_interval


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

    if sdc.lastOffsets.containsKey(entityName):
        offset = int(float(sdc.lastOffsets.get(entityName)))
    elif sdc.userParams['INITIAL_OFFSET']:
        offset = to_timestamp(datetime.strptime(sdc.userParams['INITIAL_OFFSET'], '%d/%m/%Y %H:%M'))
    else:
        offset = to_timestamp(datetime.utcnow().replace(second=0, microsecond=0) - interval)

    sdc.log.info('OFFSET: ' + str(offset))

    while True:
        if sdc.isStopped():
            break

        if sdc.userParams['QUERY_MISSING_DATA_INTERVAL'] and not sdc.isPreview():
            query_missing_data(int(offset), interval.total_seconds())

        while offset > get_now_with_delay() - interval.total_seconds():
            time.sleep(2)
            if sdc.isStopped():
                return

        cur_batch = sdc.createBatch()
        record = sdc.createRecord('record created ' + str(datetime.now()))
        sdc.log.debug('last_timestamp: {}-{}'.format(str(datetime.fromtimestamp(int(offset))), str(offset)))
        record.value = {'last_timestamp': int(offset)}
        offset += interval.total_seconds()
        cur_batch.add(record)
        cur_batch.process(entityName, str(offset))


main()
