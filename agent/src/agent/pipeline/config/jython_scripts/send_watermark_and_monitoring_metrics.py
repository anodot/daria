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
    tz = sdc.userParams['TIMEZONE'] if sdc.userParams['WATERMARK_IN_LOCAL_TIMEZONE'] == 'True' and sdc.userParams['TIMEZONE'] else 'UTC'
    return str(calendar.timegm(datetime.now(pytz.timezone(tz)).timetuple()) - watermark)


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
        err_msg = res.json().get('errors')
        if err_msg:
            raise requests.RequestException(err_msg)

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
    except requests.RequestException as e:
        sdc.error.write(record, str(e))
