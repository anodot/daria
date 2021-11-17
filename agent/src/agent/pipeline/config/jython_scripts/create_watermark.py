global sdc

try:
    sdc.importLock()
    import time
    import os
    import sys
    import calendar

    from datetime import datetime

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
    import pytz
finally:
    sdc.importUnlock()


def _get_watermark_delta(watermark):
    return str(calendar.timegm(datetime.now(pytz.utc).timetuple()) - watermark)


slept = False
for record in sdc.records:
    if record.attributes['sdc.event.type'] == 'finished-file':
        if not slept:
            # sleep a little bit to let the pipeline finish processing and sending file data
            time.sleep(int(sdc.userParams['SLEEP_TIME']))
            slept = True

        res = requests.get(sdc.userParams['CALCULATE_DIRECTORY_WATERMARK_URL'])
        res.raise_for_status()
        if not res.json():
            # we need it in the case of the first preview, when the pipeline didn't run yet
            continue
        record.value['watermark'] = float(res.json())
        record.value['schemaId'] = sdc.userParams['SCHEMA_ID']

        requests.post(sdc.userParams['FILE_PROCESSED_MONITORING_ENDPOINT'])
        requests.post(
            sdc.userParams['WATERMARK_DELTA_MONITORING_ENDPOINT'],
            params={'delta': _get_watermark_delta(record.value['watermark'])}
        )

        sdc.output.write(record)
