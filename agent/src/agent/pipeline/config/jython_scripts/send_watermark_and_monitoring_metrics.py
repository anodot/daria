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
    if not record.value['watermark'] or not record.value['schemaId']:
        sdc.log.info('The pipeline doesn\'t have watermark or schemaId, skipping sending watermark')
        continue

    try:
        # send Watermark
        res = requests.post(
            sdc.userParams['WATERMARK_URL'],
            json=record.value, proxies=sdc.userParams['PROXIES'], timeout=30
        )
        res.raise_for_status()

        # send Watermark Metrics
        res = requests.post(
            sdc.userParams['WATERMARK_DELTA_MONITORING_ENDPOINT'],
            params={'delta': _get_watermark_delta(record.value['watermark'])}
        )
        res.raise_for_status()
        requests.post(
            sdc.userParams['WATERMARK_SENT_MONITORING_ENDPOINT']
        )
        res.raise_for_status()

        sdc.output.write(record)
    except (requests.ConnectionError, requests.HTTPError) as e:
        sdc.error.write(record, str(e))
