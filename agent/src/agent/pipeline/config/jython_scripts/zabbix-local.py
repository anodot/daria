import requests
import time

entityName = ''
N_REQUESTS_TRIES = 3
ITEMS_BATCH_SIZE = 1000
HISTORIES_BATCH_SIZE = 100
last_id = None


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
                    timeout=300
                )
                res.raise_for_status()
                result = res.json()
                if 'error' in result:
                    raise Exception(str(result))
            except Exception as e:
                if i == N_REQUESTS_TRIES:
                    raise
                print(str(e))
                time.sleep(i ** 2)
                continue
            break
        return result['result']

    def _authenticate(self, user, password):
        self.auth_token = self.post('user.login', {'user': user, 'password': password})
        print('user.login - success')


client = Client('http://localhost:8888', 'Admin', 'zabbix')
items = {}


def get_now_with_delay():
    return int(time.time()) - int(0) * 60


def get_backfill_offset():
    return 1611322470


def get_interval():
    return int(300)


def get_last_processed_id():
    return last_id


def query_items_sorted():
    # returns [{itemid: val, value_type: val}, ...]
    query = {
        "search": {
            "key_": "vm.memory.size_"
        },
        'sortfield': 'itemid',
        'sortorder': 'ASC',
        'output': ['itemid', 'value_type']
    }
    data = client.post('item.get', query)
    if len(data) == 0:
        print('item.get - No data - query: ' + str(query))
    return data


def query_history(item_ids, value_type):
    histories = []
    start = time.time()
    for ids_chunk in chunks(item_ids, HISTORIES_BATCH_SIZE):
        history_params = {
            'history': value_type,
            'itemids': ids_chunk,
            'sortfield': 'clock',
            'sortorder': 'ASC',
            'time_from': end - interval,
            'time_till': end
        }
        histories += client.post('history.get', history_params)
        if len(histories) == 0:
            print('history.get - No data - query: ' + str(history_params))
    print('query_history() took ' + str(time.time() - start) + ' seconds')
    return histories


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def fetch_hosts():
    res = client.post('host.get', {'output': ['hostid', 'name']})
    if len(res) == 0:
        print('host.get - No data')
    hosts = {}
    for host in res:
        hosts[host['hostid']] = host
    return hosts


def fetch_itemids_value_types():
    global end
    start = time.time()
    itemids_value_types = query_items_sorted()
    print('query_items() took ' + str(time.time() - start) + ' seconds')

    last_processed_id = get_last_processed_id()
    if last_processed_id and int(last_processed_id) != int(itemids_value_types[-1]['itemid']):
        # this means we didn't finish processing the batch last time, because the pipeline
        # stopped or failed or smth else. So we should finish processing the previous interval
        itemids_value_types = list(filter(
            lambda x: int(x['itemid']) > int(last_processed_id),
            itemids_value_types
        ))
        end -= interval
    return itemids_value_types


def fetch_items_data(itemids):
    start = time.time()
    global items, hosts
    # itemids = list(filter(
    #     lambda x: x not in items,
    #     itemids
    # ))
    for item in client.post('item.get', {'itemids': itemids}):
        item['hostname'] = hosts[item['hostid']]['name']
        items[item['itemid']] = item
    print('fetch_items_data() took ' + str(time.time() - start) + ' seconds')


def group_ids_by_value_types(itemids_value_types):
    itemids_by_value_types = {}
    for item in itemids_value_types:
        if item['value_type'] not in itemids_by_value_types:
            itemids_by_value_types[item['value_type']] = []
        itemids_by_value_types[item['value_type']].append(item['itemid'])
    return itemids_by_value_types


interval = get_interval()
end = get_backfill_offset() + interval
hosts = fetch_hosts()


def main():
    global end, interval, last_id
    while True:
        try:
            if end > get_now_with_delay():
                time.sleep(end - get_now_with_delay())

            # they are ordered by itemid asc
            for itemids_value_types in chunks(fetch_itemids_value_types(), ITEMS_BATCH_SIZE):
                itemids = list(map(
                    lambda x: x['itemid'],
                    itemids_value_types
                ))
                fetch_items_data(itemids)

                for value_type, ids in group_ids_by_value_types(itemids_value_types).items():
                    for history in query_history(ids, value_type):
                        history.update(items[history['itemid']])

                last_id = int(itemids[-1])

            end += interval
        except Exception as e:
            raise


main()
