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


for record in sdc.records:
    watermark = record.value['watermark']
    if watermark is None:
        sdc.log.info('The pipeline doesn\'t have offset, skipping sending watermark')
        continue

    requests.post(
        sdc.userParams['WATERMARK_DELTA_MONITORING_ENDPOINT'],
        params={'delta': _get_watermark_delta(record.value['watermark'])}
    )
    requests.post(
        sdc.userParams['WATERMARK_SENT_MONITORING_ENDPOINT']
    )

    sdc.output.write(record)
