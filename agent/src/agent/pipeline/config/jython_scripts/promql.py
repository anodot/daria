global sdc

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
    import re
finally:
    sdc.importUnlock()

entityName = ''
N_REQUESTS_TRIES = 3
BATCH_SIZE = 1000


def get_now_with_delay():
    return int(time.time()) - int(sdc.userParams['DELAY_IN_MINUTES']) * 60


def get_backfill_offset():
    if sdc.lastOffsets.containsKey(entityName):
        return int(float(sdc.lastOffsets.get(entityName)))
    if sdc.userParams['INITIAL_TIMESTAMP']:
        return int(sdc.userParams['INITIAL_TIMESTAMP'])
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
            res = session.get(url_, stream=True, headers={'Accept-Encoding': 'deflate'},
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


def get_result_key(data):
    return 'values' if data['data']['resultType'] == 'matrix' else 'value'


def get_metric_name(data):
    if '__name__' not in data['metric']:
        if not sdc.userParams['AGGREGATED_METRIC_NAME']:
            raise Exception("Victoria query result doesn't contain metric __name__ and it wasn't provided by the user")
        return sdc.userParams['AGGREGATED_METRIC_NAME']
    return data['metric'].pop('__name__')


def create_base_metric(metric_name):
    base_metric_ = {
        'properties': {
            'what': metric_name,
            'target_type': 'gauge',
        },
        'tags': {},
    }
    return base_metric_


def process_matrix(result_, end_):
    i = 0
    cur_batch = sdc.createBatch()
    for result_ in result_['data']['result']:
        base_metric = create_base_metric(get_metric_name(result_))
        for dimension, value in result_['metric'].items():
            dimension = re.sub('\s+', '_', dimension.strip()).replace('.', '_')
            value = re.sub('\s+', '_', value.strip()).replace('.', '_')
            base_metric['properties'][dimension] = value
        for timestamp, value in result_[get_result_key(res)]:
            metric = base_metric
            metric['timestamp'] = int(timestamp)
            metric['value'] = value
            new_record = sdc.createRecord('record created ' + str(get_now_with_delay()))
            new_record.value = metric
            cur_batch.add(new_record)
            i += 1
            if i % BATCH_SIZE == 0:
                cur_batch.process(entityName, str(end_))
                cur_batch = sdc.createBatch()
        # if we didn't process the batch for the last time
        if i % BATCH_SIZE != 0:
            cur_batch.process(entityName, str(end_))
            cur_batch = sdc.createBatch()


def process_vector(result_, end_):
    i = 0
    cur_batch = sdc.createBatch()
    for result_ in result_['data']['result']:
        base_metric = create_base_metric(get_metric_name(result_))
        for dimension, value in result_['metric'].items():
            dimension = re.sub('\s+', '_', dimension.strip()).replace('.', '_')
            value = re.sub('\s+', '_', value).replace('.', '_')
            base_metric['properties'][dimension] = value
        timestamp, value = result_[get_result_key(res)]
        metric = base_metric
        metric['timestamp'] = end_
        metric['value'] = value
        new_record = sdc.createRecord('record created ' + str(get_now_with_delay()))
        new_record.value = metric
        cur_batch.add(new_record)
        i += 1
        if i % BATCH_SIZE == 0:
            cur_batch.process(entityName, str(end_))
            cur_batch = sdc.createBatch()
        # if we didn't process the batch for the last time
    if i % BATCH_SIZE != 0:
        cur_batch.process(entityName, str(end_))


interval = get_interval()
end = get_backfill_offset() + interval
url = sdc.userParams['URL'] + '/api/v1/query?' + urllib.urlencode({
    'query': sdc.userParams['QUERY'].encode('utf-8'),
    'timeout': sdc.userParams['QUERY_TIMEOUT'],
})

while True:
    try:
        curr_url = url + '&' + urllib.urlencode({'time': end})
        if end > get_now_with_delay():
            time.sleep(end - get_now_with_delay())
        if sdc.isStopped():
            break
        sdc.log.debug(curr_url)
        res = make_request(curr_url).json()
        sdc.log.debug(str(res))
        process_matrix(res, end) if res['data']['resultType'] == 'matrix' else process_vector(res, end)
        end += interval
    except Exception as e:
        sdc.log.error(traceback.format_exc())
        raise
