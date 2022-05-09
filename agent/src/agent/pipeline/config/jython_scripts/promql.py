global sdc

try:
    sdc.importLock()
    import sys
    import os

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
    import traceback
    import time
    import urllib
    import re
    from datetime import datetime
finally:
    sdc.importUnlock()

entityName = ''
N_REQUESTS_TRIES = 3


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
    session.headers.update(sdc.userParams['HEADERS'])
    if sdc.userParams['USERNAME']:
        session.auth = (sdc.userParams['USERNAME'], sdc.userParams['PASSWORD'])
    for i in range(1, N_REQUESTS_TRIES + 1):
        try:
            sdc.log.debug(url_)
            res = session.get(
                url_,
                stream=True,
                headers={'Accept-Encoding': 'deflate'},
                verify=bool(sdc.userParams['VERIFY_SSL']),
                timeout=sdc.userParams['QUERY_TIMEOUT']
            )
            res.raise_for_status()
        except requests.HTTPError as e:
            requests.post(sdc.userParams['MONITORING_URL'] + str(e.response.status_code))
            sdc.log.error(str(e))
            if i == N_REQUESTS_TRIES:
                raise
            time.sleep(i**2)
            continue
        break
    return res


def get_result_key(data):
    return 'values' if data['data']['resultType'] == 'matrix' else 'value'


def get_metric_name(record):
    if '__name__' not in record['metric']:
        if not sdc.userParams['AGGREGATED_METRIC_NAME']:
            raise Exception("Victoria query result doesn't contain metric __name__ and it wasn't provided by the user")
        return sdc.userParams['AGGREGATED_METRIC_NAME']
    return record['metric']['__name__']


def process_matrix(result_, end_):
    batch = sdc.createBatch()
    for res in result_['data']['result']:
        base_record = dict(res['metric'].items())
        for timestamp, value in res[get_result_key(result_)]:
            record = base_record.copy()
            record['timestamp'] = float(timestamp)
            # js 3.0 adds interval to last timestamp to send watermark, so here we should subtract it
            record['last_timestamp'] = end_ - get_interval()
            metric_name = get_metric_name(res)
            record['__name__'] = metric_name
            record['__value'] = value
            sdc_record = sdc.createRecord('record created ' + str(get_now_with_delay()))
            sdc_record.value = record
            batch.add(sdc_record)
            if batch.size == sdc.batchSize:
                batch.process(entityName, str(end_))
                batch = sdc.createBatch()
    if batch.size > 0:
        batch.process(entityName, str(end_))


def process_vector(result_, end_):
    batch = sdc.createBatch()
    for res in result_['data']['result']:
        record = dict(res['metric'].items())
        timestamp, value = res[get_result_key(result_)]
        # here timestamp and end_ are the same values
        # because aggregation functions return timestamp from the end request parameter
        record['timestamp'] = timestamp
        # js 3.0 adds interval to last timestamp to send watermark, so here we should subtract it
        record['last_timestamp'] = end_ - get_interval()
        record['__name__'] = get_metric_name(res)
        record['__value'] = value
        sdc_record = sdc.createRecord('record created ' + str(get_now_with_delay()))
        sdc_record.value = record
        batch.add(sdc_record)
        if batch.size == sdc.batchSize:
            batch.process(entityName, str(end_))
            batch = sdc.createBatch()
    if batch.size > 0:
        batch.process(entityName, str(end_))


def main():
    interval = get_interval()
    end = get_backfill_offset() + interval
    while True:
        try:
            curr_url = get_base_url() + '&' + urllib.urlencode({'time': end})
            while end > get_now_with_delay():
                time.sleep(2)
                if sdc.isStopped():
                    return
            if sdc.isStopped():
                break
            sdc.log.debug(curr_url)
            res = make_request(curr_url).json()
            sdc.log.debug(str(res))
            if res['data']['result']:
                process_matrix(res, end) if res['data']['resultType'] == 'matrix' else process_vector(res, end)
            elif sdc.userParams['DVP_ENABLED'] == 'True':
                # records with last_timestamp only
                batch = sdc.createBatch()
                record = sdc.createRecord('record created ' + str(datetime.now()))
                record.value = {'last_timestamp': end - get_interval()}
                batch.add(record)
                batch.process(entityName, str(end))
            end += interval
        except Exception:
            sdc.log.error(traceback.format_exc())
            raise


def get_base_url():
    return sdc.userParams['URL'] + '/api/v1/query?' + urllib.urlencode({
        'query': sdc.userParams['QUERY'].encode('utf-8'),
        'timeout': sdc.userParams['QUERY_TIMEOUT'],
    })


main()
