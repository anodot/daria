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
    for i in range(1, N_REQUESTS_TRIES + 1):
        try:
            sdc.log.debug(url_)
            res = requests.post(
                url_,
                stream=True,
                headers={'Content-Type': 'application/json'},
                # timeout=sdc.userParams['QUERY_TIMEOUT']
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


def get_metric_name(record):
    if '__name__' not in record['metric']:
        if not sdc.userParams['AGGREGATED_METRIC_NAME']:
            raise Exception("Victoria query result doesn't contain metric __name__ and it wasn't provided by the user")
        return sdc.userParams['AGGREGATED_METRIC_NAME']
    return record['metric']['__name__']


def process_vector(result_, end_):
    batch = sdc.createBatch()
    for res in result_['hits']['hits']:
        res['sort'] = [res['_source']['timestamp_unix_ms']]
        del res['_score']
        record = dict(res.items())
        sdc_record = sdc.createRecord('record created ' + str(get_now_with_delay()))
        sdc_record.value = record
        batch.add(sdc_record)
        if batch.size == sdc.batchSize:
            batch.process(entityName, str(end_))
            batch = sdc.createBatch()
    if batch.size > 0:
        batch.process(entityName, str(end_))


def create_record(result_, end):
    hits = result_['hits']['hits']
    batch = sdc.createBatch()
    for hit in hits:
        record = dict(hit['metric'].items())


def main():
    interval = get_interval()
    end = get_backfill_offset() + interval
    while True:
        try:
            curr_url = get_base_url()
            while end > get_now_with_delay():
                time.sleep(2)
                if sdc.isStopped():
                    return
            if sdc.isStopped():
                break
            sdc.log.debug(curr_url)
            res = make_request(curr_url).json()
            sdc.log.debug(str(res))
            if res['hits']['total']['value']:
                process_vector(res, end)
            elif sdc.userParams['DVP_ENABLED'] == 'True':
                # records with last_timestamp only
                batch = sdc.createBatch()
                record = sdc.createRecord('record created ' + str(datetime.now()))
                record.value = dict(res['hits']['hits'])
                batch.add(record)
                batch.process(entityName, str(end))
            end += interval
        except Exception:
            sdc.log.error(traceback.format_exc())
            raise


def get_base_url():
    return sdc.userParams['URLs'][0] + '/' + sdc.userParams['INDEX'] + "//_search?scroll=" \
           + sdc.userParams['SCROLL_TIMEOUT']


main()