try:
    sdc.importLock()
    import sys
    import os
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
    import traceback
    import json
    import time
    import urllib
finally:
    sdc.importUnlock()

entityName = ''
N_REQUESTS_TRIES = 3


def get_now_with_delay():
    return int(time.time()) - int(sdc.userParams['DELAY_IN_MINUTES']) * 60


def get_backfill_offset():
    if sdc.lastOffsets.containsKey(entityName):
        return int(float(sdc.lastOffsets.get(entityName)))
    days_ago = int(sdc.userParams['DAYS_TO_BACKFILL'])
    if bool(days_ago):
        return int(time.time()) - days_ago * 24 * 60 * 60
    return get_now_with_delay() - get_interval()


def get_interval():
    return int(sdc.userParams['INTERVAL'])


def make_request(url_):
    session = requests.Session()
    if sdc.userParams['USERNAME']:
        session.auth = (sdc.userParams['USERNAME'], sdc.userParams['PASSWORD'])
    for i in range(1, N_REQUESTS_TRIES + 1):
        try:
            sdc.log.debug(url_)
            res = session.get(url_, stream=True, headers={"Accept-Encoding": "deflate"},
                              verify=bool(sdc.userParams['VERIFY_SSL']), timeout=sdc.userParams['QUERY_TIMEOUT'])
            res.raise_for_status()
        except Exception as e:
            if i == N_REQUESTS_TRIES:
                raise
            sdc.log.debug(str(e))
            time.sleep(i ** 2)
            continue
        break
    return res


url = sdc.userParams['URL'] + '/api/v1/export?' + urllib.urlencode({'match': sdc.userParams['QUERY']})
interval = get_interval()
start = get_backfill_offset()
end = start + interval


while True:
    try:
        if end > get_now_with_delay():
            time.sleep(end - get_now_with_delay())
        if sdc.isStopped():
            break

        i = 0
        curr_url = url + '&start=' + str(start) + '&end=' + str(end)
        cur_batch = sdc.createBatch()
        for row in make_request(curr_url).iter_lines():
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
                metric['timestamp'] = record['timestamps'][j]
                metric['value'] = record['values'][j]
                new_record = sdc.createRecord('record created ' + str(get_now_with_delay()))
                new_record.value = metric
                cur_batch.add(new_record)
                i += 1
                # process batches of the size 1000
                if i % 1000 == 0:
                    cur_batch.process(entityName, str(end))
                    cur_batch = sdc.createBatch()
            # if we didn't process the batch for the last time
            if i % 1000 != 0:
                cur_batch.process(entityName, str(end))
                cur_batch = sdc.createBatch()
        start = end
        end += interval
    except Exception as e:
        sdc.log.error(traceback.format_exc())
        raise
