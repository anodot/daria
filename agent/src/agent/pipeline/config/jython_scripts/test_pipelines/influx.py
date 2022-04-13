global sdc

try:
    sdc.importLock()
    import sys
    import os
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import json
    import requests
    import traceback
    from datetime import datetime
    from urlparse import urlparse
finally:
    sdc.importUnlock()


def influx_request(base_url, url, method='GET', params=None, data=None, ssl=False):
    _session = requests.Session()
    request_url = "{0}/{1}".format(base_url, url)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/plain'
    }

    if isinstance(data, (dict, list)):
        data = json.dumps(data)

    return _session.request(
            method=method,
            url=request_url,
            auth=(sdc.userParams['USERNAME'], sdc.userParams['PASSWORD']),
            params=params or {},
            data=data,
            headers=headers,
            verify=ssl,
            timeout=sdc.userParams['REQUEST_TIMEOUT']
        )


try:
    influx_url_parsed = urlparse(sdc.userParams['HOST'])
    ssl = influx_url_parsed.scheme == 'https'
    params = {'q': 'SELECT * FROM ' + sdc.userParams['MEASUREMENT_NAME'], 'db': sdc.userParams['DATABASE']}
    if sdc.userParams['QUERY']:
        params = {'q': sdc.userParams['QUERY'].replace('{TIMESTAMP_CONDITION}', '1=1'), 'db': sdc.userParams['DATABASE']}

    response = influx_request(base_url=sdc.userParams['HOST'], url='query', params=params, ssl=ssl)
    sdc.log.error("influx_request Response code: {0}".format(response.status_code))
    response.raise_for_status()

    cur_batch = sdc.createBatch()
    record = sdc.createRecord('record created ' + str(datetime.now()))
    record.value = response.json()
    cur_batch.add(record)
    cur_batch.process('', str(datetime.now()))
except Exception as e:
    sdc.log.error(str(e))
    sdc.log.error(traceback.format_exc())
    raise
