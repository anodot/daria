global sdc

try:
    sdc.importLock()
    import time
    from datetime import datetime, timedelta
    import sys
    import os
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
finally:
    sdc.importUnlock()


def get_interval():
    return int(sdc.userParams['INTERVAL_IN_SECONDS'])


def get_now_with_delay():
    return int(time.time()) - int(sdc.userParams['DELAY_IN_SECONDS'])


def to_timestamp(date):
    epoch = datetime(1970, 1, 1)
    return int((date - epoch).total_seconds())


def _filter(list_):
    return list(filter(lambda x: bool(x), list_))


def csv_to_json(csv_data, last_timestamp):
    if not str(csv_data).strip():
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
    now_with_delay = get_now_with_delay() - interval.total_seconds()
    if offset > now_with_delay:
        time.sleep(offset - now_with_delay)
    start = int(offset)
    stop = int(offset + interval.total_seconds())

    session = requests.Session()
    session.headers = sdc.userParams['HEADERS']
    res = session.post(
        sdc.userParams['URL'],
        data=sdc.userParams['DATA'].format(
            start, stop
        )
    )
    res.raise_for_status()

    cur_batch = sdc.createBatch()
    for obj in csv_to_json(res.text, int(offset)):
        record = sdc.createRecord('record created ' + str(datetime.now()))
        record.value = obj
        cur_batch.add(record)
        if cur_batch.size() == sdc.batchSize:
            cur_batch.process(entityName, str(offset))
            cur_batch = sdc.createBatch()
            if sdc.isStopped():
                break
    cur_batch.process(entityName, str(offset))
    offset += interval.total_seconds()
