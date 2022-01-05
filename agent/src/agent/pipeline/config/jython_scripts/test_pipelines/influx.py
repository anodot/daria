global sdc

try:
    sdc.importLock()
    import sys
    import os
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import json
    import requests
    import traceback
finally:
    sdc.importUnlock()


def influx_request(base_url, url, method='GET', params=None, data=None, ssl=None):
    _scheme = "https" if ssl is True else "http"
    _session = requests.Session()
    request_url = "{0}/{1}".format(base_url, url)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/plain'
    }

    if isinstance(data, (dict, list)):
        data = json.dumps(data)

    try:
        response = _session.request(
            method=method,
            url=request_url,
            auth=(sdc.userParams['USERNAME'], sdc.userParams['PASSWORD']),
            params=params or {},
            data=data,
            headers=headers,
            verify=True,
        )
    except Exception:
        return None
    return response


def main():
    try:
        # get list of databases
        params = {'q': 'SHOW DATABASES', 'db': None}
        response = influx_request(base_url=sdc.userParams['HOST'], url='query', params=params, ssl=True)
        if response is None:
            raise Exception('Request to database failed')

        db_list = []
        series = response.json().get('results', [])
        for s in series:
            series_list = s.get('series')
            if series_list:
                for item in series_list:
                    db_list.extend(item['values'])

        if not any([sdc.userParams['DATABASE']] == db for db in db_list):
            raise Exception('Database %s not found. Please check your credentials again' % sdc.userParams['DATABASE'])
    except Exception as e:
        sdc.log.error(str(e))
        sdc.log.error(traceback.format_exc())
        raise


main()
