global sdc

try:
    sdc.importLock()
    import sys
    import os
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    from datetime import datetime, timedelta
    import requests
    import traceback
finally:
    sdc.importUnlock()


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


def main():
    session = requests.Session()
    session.headers = sdc.userParams['HEADERS']
    try:
        if sdc.userParams['INITIAL_OFFSET']:
            offset = to_timestamp(datetime.strptime(sdc.userParams['INITIAL_OFFSET'], '%d/%m/%Y %H:%M'))
        else:
            offset = to_timestamp(datetime.utcnow().replace(second=0, microsecond=0) - timedelta(days=365))

        res = session.post(
            sdc.userParams['URL'],
            data=sdc.userParams['QUERY'].format(int(offset), 'now()'),
            timeout=sdc.userParams['TIMEOUT']
        )
        res.raise_for_status()
        cur_batch = sdc.createBatch()
        for obj in csv_to_json(res.text, int(offset))[:10]:
            record = sdc.createRecord('record created ' + str(datetime.now()))
            record.value = obj
            cur_batch.add(record)
        cur_batch.process('', str(offset))
    except Exception as e:
        sdc.log.error(str(e))
        sdc.log.error(traceback.format_exc())
        raise


main()
