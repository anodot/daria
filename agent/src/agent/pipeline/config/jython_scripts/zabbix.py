global sdc

try:
    sdc.importLock()
    import sys
    import os
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
    import traceback
    import time
finally:
    sdc.importUnlock()

entityName = ''
N_REQUESTS_TRIES = 3
BATCH_SIZE = 1000


class Client:
    def __init__(self, url, user, password):
        self.url = url + '/api_jsonrpc.php'
        self.auth_token = None
        self._authenticate(user, password)

    def post(self, method, params):
        for i in range(1, N_REQUESTS_TRIES + 1):
            try:
                res = requests.post(self.url, json={
                    'jsonrpc': '2.0',
                    'method': method,
                    'params': params,
                    'id': 1,
                    'auth': self.auth_token,
                })
                res.raise_for_status()
                result = res.json()
                if 'error' in result:
                    raise Exception(str(result))
            except Exception as e:
                if i == N_REQUESTS_TRIES:
                    raise
                sdc.log.debug(str(e))
                time.sleep(i ** 2)
                continue
            break
        return result['result']

    def _authenticate(self, user, password):
        self.auth_token = self.post('user.login', {'user': user, 'password': password})


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


interval = get_interval()
end = get_backfill_offset() + interval

client = Client(sdc.userParams['URL'], sdc.userParams['USER'], sdc.userParams['PASSWORD'])

while True:
    try:
        if end > get_now_with_delay():
            time.sleep(end - get_now_with_delay())
        if sdc.isStopped():
            break
        batch = sdc.createBatch()
        for item in client.post('item.get', sdc.userParams['PARAMS']):
            history = client.post('history.get', {
                'history': item['value_type'],
                'itemids': item['itemid'],
                'sortfield': 'clock',
                'sortorder': 'ASC',
                'time_from': end - interval,
                'time_till': end,
            })
            history.update(item)
            batch.add(history)
        batch.process(entityName, str(end))

        end += interval
    except Exception as e:
        sdc.log.error(traceback.format_exc())
        raise
