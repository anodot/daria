global sdc

try:
    sdc.importLock()
    import time
    import os
    import sys

    from datetime import datetime

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
    import pytz
    import calendar
finally:
    sdc.importUnlock()


def _get_watermark_delta(watermark):
    dt = datetime.now(pytz.timezone(sdc.userParams['TIMEZONE'])).astimezone(pytz.utc)
    return str(calendar.timegm(dt.timetuple()) - watermark)


slept = False
for record in sdc.records:
    if record.attributes['sdc.event.type'] == 'finished-file':
        if not slept:
            # sleep a little bit to let the pipeline finish processing and sending file data
            time.sleep(int(sdc.userParams['SLEEP_TIME']))
            slept = True

        res = requests.get(sdc.userParams['PIPELINE_OFFSET_URL'])
        res.raise_for_status()
        if not res.json():
            continue
        record.value['watermark'] = float(res.json()) + float(sdc.userParams['BUCKET_SIZE_IN_SECONDS'])
        record.value['schemaId'] = sdc.userParams['SCHEMA_ID']

        requests.post(sdc.userParams['FILE_PROCESSED_MONITORING_ENDPOINT'])
        requests.post(
            sdc.userParams['WATERMARK_DELTA_MONITORING_ENDPOINT'] + _get_watermark_delta(record.value['watermark'])
        )

        sdc.output.write(record)
