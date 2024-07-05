global sdc

try:
    sdc.importLock()
    import sys
    import os
    import time
    import gc

    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))

    from datetime import datetime
    import requests
finally:
    sdc.importUnlock()

DATEFORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


def to_timestamp(date):
    epoch = datetime(1970, 1, 1)
    return (date - epoch).total_seconds()


N_REQUESTS_TRIES = 3

for record in sdc.records:
    offset = record.value['last_timestamp']

    session = requests.Session()
    for i in range(1, N_REQUESTS_TRIES + 1):
        try:
            res = requests.get(sdc.userParams['AGENT_DATA_EXTRACTOR_URL'],
                               params={'offset': offset},
                               timeout=sdc.userParams['TIMEOUT'])
            res.raise_for_status()
            for idx, obj in enumerate(res.json()):
                new_record = sdc.createRecord('record created ' + str(idx))
                new_record.value = obj
                sdc.output.write(new_record)
                if idx == 10 and sdc.isPreview():
                    break
            break
        except requests.HTTPError as e:
            requests.post(sdc.userParams['MONITORING_URL'] + str(e.response.status_code))
            sdc.log.error(str(e))
            if i == N_REQUESTS_TRIES:
                raise
            time.sleep(2 ** i)


gc.collect()
