global sdc

try:
    sdc.importLock()
    import time
    import os
    import sys

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import pytz

    from datetime import datetime, timedelta
finally:
    sdc.importUnlock()


def main():
    slept = False
    for record in sdc.records:
        if not slept:
            # sleep a little to let the pipeline finish processing and sending file data
            time.sleep(int(sdc.userParams['SLEEP_TIME']))
            slept = True
        # watermark contains the end of the current interval
        watermark = to_timestamp(get_next_bucket_start(sdc.userParams['BUCKET_SIZE'], record.value['watermark']))
        record.value['watermark'] = watermark
        record.value['schemaId'] = sdc.userParams['SCHEMA_ID']
        sdc.output.write(record)


def to_timestamp(date):
    epoch = datetime(1970, 1, 1, tzinfo=pytz.utc)
    return int((date - epoch).total_seconds())


def get_next_bucket_start(bs, offset):
    dt = datetime.fromtimestamp(offset, tz=pytz.utc)
    if bs == '1m':
        return dt.replace(second=0, microsecond=0) + timedelta(minutes=1)
    elif bs == '5m':
        return dt.replace(second=0, microsecond=0) + timedelta(minutes=5 - dt.minute % 5)
    elif bs == '1h':
        return dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    elif bs == '1d':
        return dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    raise Exception('Invalid bucket size provided')


main()
