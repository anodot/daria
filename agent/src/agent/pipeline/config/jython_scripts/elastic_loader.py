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


def retry_request(func):
    def wrap(*args, **kwargs):
        for i in range(1, N_REQUESTS_TRIES + 1):
            try:
                return func(*args, **kwargs)
            except elasticsearch.exceptions.ElasticsearchException as e:
                sdc.log.error(str(e))
                if i == N_REQUESTS_TRIES:
                    raise
                time.sleep(i ** 2)
                continue

    return wrap


@retry_request
def make_search(client, index, params={}, scroll=None):
    return client.search(
                body=params,
                index=index,
                scroll=scroll,
                timeout=sdc.userParams['QUERY_TIMEOUT']
            )


@retry_request
def make_scroll(client, sid, scroll):
    return client.scroll(scroll_id=sid, scroll=scroll)


def make_request(client, index, params={}, scroll=None):
    page = make_search(client, index, params, scroll)
    sid = page['_scroll_id']
    scroll_size = page['hits']['total']['value']
    yield page
    while scroll_size:
        page = make_scroll(client, sid, scroll)
        sid = page['_scroll_id']
        scroll_size = len(page['hits']['hits'])
        if scroll_size:
            yield page
    client.clear_scroll(scroll_id=sid)


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
            for batch in make_request(
                    client,
                    sdc.userParams['INDEX'],
                    get_query_params(end, interval),
                    sdc.userParams.get('SCROLL_TIMEOUT')
                ):
                sdc.log.debug(str(batch))
                if len(batch['hits']['hits']):
                    process_batch(batch, end)
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
    basic_auth = None if not sdc.userParams['USERNAME'] else (sdc.userParams['USERNAME'], sdc.userParams['PASSWORD'])
    return elasticsearch.Elasticsearch(
        sdc.userParams['URLs'],
        basic_auth=basic_auth,
        verify_certs=bool(sdc.userParams['VERIFY_SSL'])
    )


def get_query_params(offset, interval):
    return json.loads(
        str(sdc.userParams['QUERY']
            ).replace(
            '"$OFFSET+$INTERVAL"', str(offset + interval)
        ).replace(
            '"$OFFSET"', str(offset))
    )


main()
