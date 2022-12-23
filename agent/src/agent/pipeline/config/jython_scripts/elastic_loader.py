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
    import json
    from datetime import datetime
    import elasticsearch
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


def make_request(client, index, params={}, scroll=None):
    for i in range(1, N_REQUESTS_TRIES + 1):
        try:
            sdc.log.debug(index)
            res = client.search(
                body=params,
                index=index,
                scroll=scroll,
                timeout=sdc.userParams['QUERY_TIMEOUT']
            )
        except elasticsearch.exceptions.HTTP_EXCEPTIONS as e:
            requests.post(sdc.userParams['MONITORING_URL'] + str(e.response.status_code))
            sdc.log.error(str(e))
            if i == N_REQUESTS_TRIES:
                raise
            time.sleep(i**2)
            continue
        break
    return res


def process_batch(result_, end_):
    batch = sdc.createBatch()
    for res in result_['hits']['hits']:
        record = dict(res.items())
        record['last_timestamp'] = end_ - get_interval()
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
    client = get_client()
    while True:
        try:
            while end > get_now_with_delay():
                time.sleep(2)
                if sdc.isStopped():
                    return
            if sdc.isStopped():
                break
            res = make_request(
                client,
                sdc.userParams['INDEX'],
                get_query_params(end),
                sdc.userParams.get('SCROLL_TIMEOUT')
            )
            sdc.log.debug(str(res))
            if res['hits']['total']['value']:
                process_batch(res, end)
            elif sdc.userParams['DVP_ENABLED'] == 'True':
                # records with last_timestamp only
                batch = sdc.createBatch()
                record = sdc.createRecord('record created ' + str(datetime.now()))
                record.value = dict()
                record.value['last_timestamp'] = end - get_interval()
                batch.add(record)
                batch.process(entityName, str(end))
            end += interval
        except Exception:
            sdc.log.error(traceback.format_exc())
            raise


def get_client():
    return elasticsearch.Elasticsearch(
        sdc.userParams['URLs']
    )


def get_query_params(offset):
    return json.loads(str(sdc.userParams['QUERY']).replace('"$OFFSET"', str(offset)))


main()
