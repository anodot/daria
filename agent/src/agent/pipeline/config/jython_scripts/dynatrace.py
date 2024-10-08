global sdc

try:
    sdc.importLock()
    import sys
    import os
    import time
    import traceback
    import re
    from urllib import urlencode
    from urlparse import urljoin

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests

    from datetime import datetime, timedelta
finally:
    sdc.importUnlock()

# single threaded - no entityName because we need only one offset
entityName = ''
DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'
N_REQUESTS_TRIES = 5

query_size = int(sdc.userParams.get('QUERY_SIZE', 1000))

# because user specifies the interval in minutes
interval = timedelta(seconds=int(float(sdc.userParams['INTERVAL_IN_MINUTES']) * 60))
delay = timedelta(minutes=int(sdc.userParams['DELAY']))
days_to_backfill = timedelta(days=int(sdc.userParams['DAYS_TO_BACKFILL']))
sdc.log.info('INTERVAL_IN_MINUTES: ' + str(interval))
sdc.log.info('DELAY: ' + str(delay))
sdc.log.info('DAYS_TO_BACKFILL: ' + str(days_to_backfill))


# Jython converts datetime objects to java.sql.Timestamp when assigning it to a variable
def date_from_str(date):
    return datetime.strptime(date, DATEFORMAT)


def date_to_str(date):
    return date.strftime(DATEFORMAT)


def build_url():
    base_url = urljoin(sdc.userParams['DYNATRACE_URL'], "api/v2/metrics/query")
    params = {
        "metricSelector": sdc.userParams['QUERY'],
        "resolution": sdc.userParams['RESOLUTION'],
    }
    query_string = urlencode(params)
    return base_url + "?" + query_string


def main():
    # get previously committed offset or use 0
    if sdc.lastOffsets.containsKey(entityName):
        offset = sdc.lastOffsets.get(entityName)
    elif days_to_backfill.total_seconds() > 0:
        offset = date_to_str(datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - days_to_backfill)
    else:
        offset = date_to_str(datetime.utcnow().replace(second=0, microsecond=0) - interval)

    sdc.log.info('Start offset: ' + str(offset))

    cur_batch = sdc.createBatch()
    dynatrace_url = build_url()
    sdc.log.debug("Dynatrace query URL: " + dynatrace_url)

    while True:
        start_time = time.time()
        try:
            end_time = date_to_str(date_from_str(offset) + interval)
            latest_date = date_to_str(datetime.utcnow().replace(second=0, microsecond=0) - delay)
            watermark_ts = (date_from_str(offset) - datetime(1970, 1, 1)).total_seconds()
            while (date_from_str(end_time) - date_from_str(latest_date)).total_seconds() > time.time() - start_time:
                time.sleep(2)
                if sdc.isStopped():
                    return cur_batch, offset

            last = None
            while True:
                skip = False
                for i in range(1, N_REQUESTS_TRIES + 1):
                    try:
                        #sdc.log.debug(str(body))
                        res = requests.get(
                            dynatrace_url,
                            headers={
                                'Authorization': 'Api-Token ' + sdc.userParams['DYNATRACE_TOKEN'],
                            },
                            timeout=180
                        )
                        res.raise_for_status()
                        sdc.log.debug(str(res.json()))
                        break
                    except requests.HTTPError as e:
                        requests.post(sdc.userParams['MONITORING_URL'] + str(e.response.status_code))
                        sdc.log.error(str(e))
                        if i == N_REQUESTS_TRIES:
                            if e.response.status_code == 504:
                                # sdc.log.info(str(body))
                                skip = True
                                break
                            raise
                        time.sleep(3 ** i)

                if skip:
                    break

                data = res.json()
                sdc.log.debug("totalCount" + str(data.get("totalCount", -1)))
                if data["metrics"]:
                    # records with data
                    for metric in data["metrics"]:
                        if '@timestamp' not in metric:
                            metric['@timestamp'] = offset
                        metric['@timestamp'] = re.sub(r'(\.[0-9]+)', '', metric['@timestamp'])
                        metric['last_timestamp'] = watermark_ts
                        record = sdc.createRecord('record created ' + str(datetime.now()))
                        record.value = metric
                        cur_batch.add(record)
                elif sdc.userParams['DVP_ENABLED'] == 'True':
                    # records with last_timestamp only
                    record = sdc.createRecord('record created ' + str(datetime.now()))
                    record.value = {'last_timestamp': watermark_ts}
                    cur_batch.add(record)
                break

            # send batch and save offset
            offset = end_time
            cur_batch.process(entityName, offset)
            cur_batch = sdc.createBatch()
            # if the pipeline has been stopped, we should end the script
            if sdc.isStopped():
                return cur_batch, offset

            # sleep_time = int(sdc.userParams['INTERVAL_IN_MINUTES']) * 60 - (time.time() - time_start)
            # sdc.log.info('Sleep time: ' + str(sleep_time))
            # time.sleep(sleep_time)
        except Exception:
            sdc.log.error(traceback.format_exc())
            raise


cur_batch_, offset_ = main()
if cur_batch_.size() + cur_batch_.errorCount() > 0:
    cur_batch_.process(entityName, str(offset_))
