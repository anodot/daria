global sdc

try:
    sdc.importLock()
    import time
    from datetime import datetime, timedelta
    import sys
    import os
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
    import pytz
finally:
    sdc.importUnlock()


def get_interval():
    return int(sdc.userParams['INTERVAL_IN_SECONDS'])


def get_now():
    return int(time.time())


def to_timestamp(date):
    epoch = datetime(1970, 1, 1)
    return int((date - epoch).total_seconds())


def prtg_ts_to_unix_ts(prtg_ts, tz=pytz.timezone(sdc.userParams['TIMEZONE'])):
    return datetime.fromtimestamp((prtg_ts - 25569) * 86400, tz=tz)


def _filter(list_):
    return list(filter(lambda x: bool(x), list_))


def csv_to_json(csv_data, last_timestamp):
    if not str(csv_data.encode('utf-8')).strip():
        return []
    results = _filter(csv_data.split('\r\n\r\n'))
    data = []
    for result in results:
        rows = result.split('\r\n')
        header = _filter(rows.pop(0).split(','))
        for row in rows:
            rec = dict(zip(header, _filter(row.split(','))))
            rec['last_timestamp'] = last_timestamp
            data.append(rec)
    return data


entityName = ''


def main():
    interval = timedelta(seconds=get_interval())
    if sdc.lastOffsets.containsKey(entityName):
        offset = int(float(sdc.lastOffsets.get(entityName)))
    else:
        offset = to_timestamp(datetime.utcnow().replace(minute=0, second=0, microsecond=0))

    sdc.log.info('OFFSET: ' + str(offset))

    while True:
        if sdc.isStopped():
            break
        while offset > get_now():
            time.sleep(1)
            if sdc.isStopped():
                return

        session = requests.Session()
        if sdc.userParams['USERNAME']:
            session.auth = (sdc.userParams['USERNAME'], sdc.userParams['PASSWORD'])
        if offset - get_interval() < get_now():
            offset = get_now() + get_interval()
        try:
            res = session.get(sdc.userParams['URL'], verify=sdc.userParams['VERIFY_SSL'])
            res.raise_for_status()
        except requests.HTTPError as e:
            requests.post(sdc.userParams['MONITORING_URL'] + str(e.response.status_code))
            sdc.log.error(str(e))

        cur_batch = sdc.createBatch()
        record = sdc.createRecord('record created ' + str(datetime.now()))
        record.value = {'last_timestamp': int(offset)}
        cur_batch.add(record)
        cur_batch.process(entityName, str(offset))
        offset += interval.total_seconds()


main()
