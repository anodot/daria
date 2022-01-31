global sdc

try:
    sdc.importLock()
    import sys
    import os
    import time
    import urlparse
    import traceback
    import re

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests

    from datetime import datetime, timedelta, tzinfo
finally:
    sdc.importUnlock()

# single threaded - no entityName because we need only one offset
entityName = ''
DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'

query_size = int(sdc.userParams.get('QUERY_SIZE', 1000))

# because user specifies the interval in minutes
interval = timedelta(seconds=int(float(sdc.userParams['INTERVAL']) * 60))
delay = timedelta(minutes=int(sdc.userParams['DELAY']))
days_to_backfill = timedelta(days=int(sdc.userParams['DAYS_TO_BACKFILL']))
sdc.log.info('INTERVAL: ' + str(interval))
sdc.log.info('DELAY: ' + str(delay))
sdc.log.info('DAYS_TO_BACKFILL: ' + str(days_to_backfill))


# Jython converts datetime objects to java.sql.Timestamp when assigning it to a variable
def date_from_str(date):
    return datetime.strptime(date, DATEFORMAT)


def date_to_str(date):
    return date.strftime(DATEFORMAT)


# get previously committed offset or use 0
if sdc.lastOffsets.containsKey(entityName):
    offset = sdc.lastOffsets.get(entityName)
elif days_to_backfill.total_seconds() > 0:
    offset = date_to_str(datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - days_to_backfill)
else:
    offset = date_to_str(datetime.utcnow().replace(second=0, microsecond=0) - interval)

sdc.log.info('Start offset: ' + str(offset))

# get record prefix from user parameters or default to empty string
if sdc.userParams.containsKey('recordPrefix'):
    prefix = sdc.userParams.get('recordPrefix')
else:
    prefix = ''

cur_batch = sdc.createBatch()

N_REQUESTS_TRIES = 5

while True:
    start_time = time.time()
    try:
        end_time = date_to_str(date_from_str(offset) + interval)
        latest_date = date_to_str(datetime.utcnow().replace(second=0, microsecond=0) - delay)
        sleep = (date_from_str(end_time) - date_from_str(latest_date)).total_seconds() - (time.time() - start_time)
        if sleep > 0:
            sdc.log.debug('Sleep time: ' + str(sleep))
            time.sleep(sleep)

        last = None
        while True:
            body = {
                "query": sdc.userParams['QUERY'],
                "startTime": offset,
                "endTime": end_time,
                "size": query_size,
                "after": last
            }
            skip = False
            for i in range(1, N_REQUESTS_TRIES + 1):
                try:
                    sdc.log.debug(str(body))
                    res = requests.post(sdc.userParams['SAGE_URL'],
                                        headers={
                                            'Authorization': 'Bearer ' + sdc.userParams['SAGE_TOKEN'],
                                            'Source': 'anodot'
                                        },
                                        json=body, verify=False, timeout=180)

                    res.raise_for_status()
                    sdc.log.debug(str(res.json()))
                    break
                except requests.HTTPError as e:
                    event = sdc.createEvent('sage_error', 1)
                    event.value = {
                        'value': 1,
                        'properties': {
                            'what': 'sage_http_error',
                            'target_type': 'counter',
                            'code': e.response.status_code,
                            'pipeline_name': sdc.userParams['PIPELINE_NAME']
                        },
                        'timestamp': time.time()
                    }
                    cur_batch.addEvent(event)
                    cur_batch.process(entityName, offset)
                    cur_batch = sdc.createBatch()
                    sdc.log.error(str(e))
                    if i == N_REQUESTS_TRIES:
                        if e.response.status_code == 504:
                            sdc.log.info(str(body))
                            skip = True
                            break

                        raise

                    time.sleep(3 ** i)

            if skip:
                break

            data = res.json()
            for hit in data["hits"]:
                if '@timestamp' not in hit:
                    hit['@timestamp'] = offset
                hit['@timestamp'] = re.sub(r'(\.[0-9]+)', '', hit['@timestamp'])
                record = sdc.createRecord('record created ' + str(datetime.now()))
                record.value = hit
                cur_batch.add(record)

            # last = data.get('last', None)
            # if last is None:
            #     break

            # cur_batch.process(entityName, data["hits"][-1]['@timestamp'])
            # cur_batch = sdc.createBatch()
            break

        # send batch and save offset
        offset = end_time
        cur_batch.process(entityName, offset)
        cur_batch = sdc.createBatch()
        # if the pipeline has been stopped, we should end the script
        if sdc.isStopped():
            break

        # sleep_time = int(sdc.userParams['INTERVAL']) * 60 - (time.time() - time_start)
        # sdc.log.info('Sleep time: ' + str(sleep_time))
        # time.sleep(sleep_time)
    except Exception as e:
        sdc.log.error(traceback.format_exc())
        raise

if cur_batch.size() + cur_batch.errorCount() + cur_batch.eventCount() > 0:
    cur_batch.process(entityName, str(offset))