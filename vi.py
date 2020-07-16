try:
    sdc.importLock()
    import sys
    import os
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
    import traceback
    import json
    import time
finally:
    sdc.importUnlock()

entityName = ''
N_REQUESTS_TRIES = 3

def get_now():
    return int(time.time())


def get_backfill_offset():
    # if sdc.lastOffsets.containsKey(entityName):
    #     raise Exception(sdc.lastOffsets.get(entityName))
    #     return int(float(sdc.lastOffsets.get(entityName)))
    days_ago = int(sdc.userParams['DAYS_TO_BACKFILL'])
    if bool(days_ago):
        return get_now() - days_ago * 24 * 60 * 60
    return get_now() - get_interval()


def get_interval():
    return int(sdc.userParams['INTERVAL'])


def make_request(url_, user, password):
    session = requests.Session()
    session.auth = (user, password)
    for i in range(1, N_REQUESTS_TRIES + 1):
        try:
            sdc.log.debug(url_)
            res = session.get(url_, stream=True)
            res.raise_for_status()
        except Exception as e:
            if i == N_REQUESTS_TRIES:
                raise
            sdc.log.debug(str(e))
            time.sleep(i ** 2)
        break
    return res


url = sdc.userParams['URL'] + '/api/v1/export?' + sdc.userParams['QUERY']
interval = get_interval()
start = get_backfill_offset()
end = start + interval


try:
    while True:
        if end > get_now():
            time.sleep(end - get_now())
        if sdc.isStopped():
            break

        curr_url = url + '&start=' + str(start) + '&end=' + str(end)

        for row in make_request(curr_url, sdc.userParams['USERNAME'], sdc.userParams['PASSWORD']).iter_lines():
            cur_batch = sdc.createBatch()
            record = json.loads(row.decode("utf-8"))
            sdc.log.debug(row)
            base_metric = {
                "properties": {
                    "what": record['metric'].pop('__name__'),
                    'target_type': "gauge",
                },
                "tags": {

                },
            }
            for dimension, value in record['metric'].items():
                base_metric['properties'][dimension] = value
            for j in range(len(record['timestamps'])):
                metric = base_metric
                # raise Exception(record['timestamps'][j])
                metric['timestamp'] = record['timestamps'][j]
                metric['value'] = record['values'][j]
                new_record = sdc.createRecord('record created ' + str(get_now()))
                new_record.value = metric
                cur_batch.add(new_record)
            cur_batch.process(entityName, str(end))
            raise Exception(record['timestamps'])
        start = end
        end += interval
except Exception as e:
    sdc.log.error(traceback.format_exc())
    raise
