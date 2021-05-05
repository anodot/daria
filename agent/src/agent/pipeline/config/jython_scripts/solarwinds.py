global sdc

try:
    sdc.importLock()
    import sys
    import os
    import time
    import traceback

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests

    from datetime import datetime, timedelta
    from requests.auth import HTTPBasicAuth
finally:
    sdc.importUnlock()

# single threaded - no entityName because we need only one offset
entityName = ''
DATEFORMAT = sdc.userParams['DATEFORMAT']
SOLARWINDS_API_ADDRESS = '/SolarWinds/InformationService/v3/Json/Query'
LAST_TIMESTAMP = '%last_timestamp%'


# Jython converts datetime objects to java.sql.Timestamp when assigning it to a variable
def date_from_str(date):
    return datetime.strptime(date, DATEFORMAT)


def date_to_str(date):
    return date.strftime(DATEFORMAT)


def get_now_with_delay():
    return int(time.time()) - int(sdc.userParams['DELAY_IN_SECONDS'])


def to_timestamp(date):
    epoch = datetime(1970, 1, 1)
    return int((date - epoch).total_seconds())


def get_interval():
    return int(sdc.userParams['INTERVAL_IN_SECONDS'])


# get previously committed offset or use 0
if sdc.lastOffsets.containsKey(entityName):
    offset = int(float(sdc.lastOffsets.get(entityName)))
elif sdc.userParams['DAYS_TO_BACKFILL']:
    offset = to_timestamp(datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=int(sdc.userParams['DAYS_TO_BACKFILL'])))
else:
    offset = to_timestamp(datetime.now().replace(second=0, microsecond=0))

sdc.log.info('Start offset: ' + str(offset))

cur_batch = sdc.createBatch()

N_REQUESTS_TRIES = 3

while True:
    try:
        end = offset + get_interval()
        if end > get_now_with_delay():
            time.sleep(end - get_now_with_delay())
        query = sdc.userParams['QUERY'].replace(LAST_TIMESTAMP, date_to_str(datetime.fromtimestamp(offset)))

        for i in range(1, N_REQUESTS_TRIES + 1):
            try:
                res = requests.get(
                    sdc.userParams['SOLARWINDS_API_URL'] + SOLARWINDS_API_ADDRESS,
                    auth=HTTPBasicAuth(sdc.userParams['API_USER'], sdc.userParams['API_PASSWORD']),
                    params={'query': query},
                    verify=False, timeout=180,
                )
                res.raise_for_status()
                break
            except requests.HTTPError as e:
                event = sdc.createEvent('sage_error', 1)
                event.value = {
                    'value': 1,
                    'properties': {
                        'what': 'solarwinds_http_error',
                        'target_type': 'gauge',
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
                    raise
                time.sleep(2 ** i)

        for row in res.json()['results']:
            record = sdc.createRecord('record created ' + str(datetime.now()))
            record.value = row
            cur_batch.add(record)

        # send batch and save offset
        offset = end
        cur_batch.process(entityName, str(offset))
        cur_batch = sdc.createBatch()
        if sdc.isStopped():
            break
    except Exception as e:
        sdc.log.error(traceback.format_exc())
        raise

if cur_batch.size() + cur_batch.errorCount() + cur_batch.eventCount() > 0:
    cur_batch.process(entityName, str(offset))