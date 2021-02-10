global sdc

try:
    sdc.importLock()
    import sys
    import os
    sys.path.append(os.path.join(os.environ['SDC_DIST'], 'python-libs'))
    import requests
    import traceback
    import time
    import json
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
                res = requests.post(
                    self.url,
                    json={
                        'jsonrpc': '2.0',
                        'method': method,
                        'params': params,
                        'id': 1,
                        'auth': self.auth_token
                    },
                    headers={
                        'Content-Type': 'application/json-rpc'
                    },
                    timeout=sdc.userParams['QUERY_TIMEOUT']
                )
                res.raise_for_status()
                result = res.json()
                if 'error' in result:
                    raise Exception(str(result))
            except Exception as e:
                if i == N_REQUESTS_TRIES:
                    raise
                sdc.log.info(str(e))
                time.sleep(i ** 2)
                continue
            break
        return result['result']

    def _authenticate(self, user, password):
        self.auth_token = self.post('user.login', {'user': user, 'password': password})
        sdc.log.info('user.login - success')


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


def query_items_by_host(host_id, zabbix_client):
    # items: { itemid: item }
    items = {}
    # itemids: { value_type: [id1, id2 ...] }
    itemids_by_value_type = {}

    query = json.loads(sdc.userParams['QUERY'])
    query['hostids'] = host_id
    data = zabbix_client.post('item.get', query)
    if len(data) == 0:
        sdc.log.info('item.get - No data - query: ' + str(query))

    for item in data:
        if item['value_type'] not in itemids_by_value_type:
            itemids_by_value_type[item['value_type']] = []

        itemids_by_value_type[item['value_type']].append(item['itemid'])
        items[item['itemid']] = item

    return items, itemids_by_value_type


interval = get_interval()
end = get_backfill_offset() + interval
sdc.log.info('INTERVAL: ' + str(interval))
sdc.log.info('TIME_TO: ' + str(end))
client = Client(sdc.userParams['URL'], sdc.userParams['USER'], sdc.userParams['PASSWORD'])

while True:
    try:
        if end > get_now_with_delay():
            time.sleep(end - get_now_with_delay())
        if sdc.isStopped():
            break
        batch = sdc.createBatch()

        hosts = client.post('host.get', {'output': ['hostid', 'name']})
        if len(hosts) == 0:
            sdc.log.info('host.get - No data')

        for host in hosts:
            items, itemids_by_value_type = query_items_by_host(host['hostid'], client)
            for value_type, ids in itemids_by_value_type.items():
                history_params = {
                    'history': value_type,
                    'itemids': ids,
                    'sortfield': 'clock',
                    'sortorder': 'ASC',
                    'time_from': end - interval,
                    'time_till': end
                }
                histories = client.post('history.get', history_params)
                # add fields from item to every history record
                if len(histories) == 0:
                    sdc.log.info('history.get - No data - query: ' + str(history_params))
                for history in histories:
                    history.update(items[history['itemid']])
                    history['host'] = host['name']
                    record = sdc.createRecord('record created ' + str(get_now_with_delay()))
                    record.value = history
                    batch.add(record)

        batch.process(entityName, str(end))

        end += interval
    except Exception as e:
        sdc.log.error(traceback.format_exc())
        raise
