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
    import re
finally:
    sdc.importUnlock()

entityName = ''
N_REQUESTS_TRIES = 3
SLEEP_INTERVAL_SECONDS = 10
LOG_EVERYTHING = sdc.userParams['LOG_EVERYTHING']


def extra_log(text):
    if LOG_EVERYTHING:
        sdc.log.info(str(text))


class Client:
    def __init__(self, url, user, password):
        self.url = url + '/api_jsonrpc.php'
        self.auth_token = None
        self.session = requests.Session()
        self._authenticate(user, password)

    def post(self, method, params):
        for i in range(1, N_REQUESTS_TRIES + 1):
            try:
                request = {
                    'jsonrpc': '2.0',
                    'method': method,
                    'params': params,
                    'id': 1,
                    'auth': self.auth_token
                }
                extra_log(request)
                res = self.session.post(
                    self.url,
                    json=request,
                    headers={
                        'Content-Type': 'application/json-rpc'
                    },
                    timeout=sdc.userParams['QUERY_TIMEOUT'],
                    verify=bool(sdc.userParams.get('VERIFY_SSL', True))
                )
                extra_log(res.text)
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


client = Client(sdc.userParams['URL'], sdc.userParams['USER'], sdc.userParams['PASSWORD'])


def get_now_with_delay():
    return int(time.time()) - int(sdc.userParams['DELAY_IN_MINUTES']) * 60


def get_backfill_offset():
    if sdc.lastOffsets.containsKey(entityName):
        offset = sdc.lastOffsets.get(entityName).split('_')[0]
        return int(float(offset))
    if sdc.userParams['INITIAL_TIMESTAMP']:
        return int(sdc.userParams['INITIAL_TIMESTAMP'])
    return get_now_with_delay() - get_interval()


def get_interval():
    return int(sdc.userParams['INTERVAL'])


def get_last_processed_id():
    if sdc.lastOffsets.containsKey(entityName):
        parts = sdc.lastOffsets.get(entityName).split('_')
        if len(parts) == 2:
            return parts[1]
    return None


def query_history(item_ids, value_type_, end):
    for ids_chunk in chunks(item_ids, int(sdc.userParams['HISTORIES_BATCH_SIZE'])):
        history_params = {
            'history': value_type_,
            'itemids': ids_chunk,
            'sortfield': 'clock',
            'sortorder': 'ASC',
            'time_from': end - get_interval(),
            'time_till': end - 1
        }
        histories = client.post('history.get', history_params)
        # add fields from item to every history record
        if len(histories) == 0:
            sdc.log.info('history.get - No data for chunk - query: ' + str(history_params))
            continue
        yield histories


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def fetch_hosts():
    res = client.post('host.get', {'output': ['hostid', 'name']})
    if len(res) == 0:
        sdc.log.info('host.get - No data')
    return {host['hostid']: host for host in res}


def fetch_itemids_value_types(end):
    query = json.loads(sdc.userParams['QUERY'])
    query['output'] = ['itemid', 'value_type']
    query['sortfield'] = 'itemid'

    start = time.time()
    itemids_value_types = client.post('item.get', query)
    sdc.log.debug('query_items() took ' + str(time.time() - start) + ' seconds')
    sdc.log.debug('we got ' + str(len(itemids_value_types)) + ' items')
    if len(itemids_value_types) == 0:
        sdc.log.info('item.get - No data - query: ' + str(json.loads(sdc.userParams['QUERY'])))
        return []

    last_processed_id = get_last_processed_id()
    if last_processed_id and int(last_processed_id) != int(itemids_value_types[-1]['itemid']):
        # this means we didn't finish processing the batch last time, because the pipeline
        # stopped or failed or smth else. So we should finish processing the previous interval
        itemids_value_types = list(filter(
            lambda x: int(x['itemid']) > int(last_processed_id),
            itemids_value_types
        ))
        end -= get_interval()
    return itemids_value_types


def fetch_items_data(itemids_):
    hosts = fetch_hosts()
    start = time.time()
    items_ = {}
    params = {'itemids': itemids_}
    query = json.loads(sdc.userParams['QUERY'])
    if 'output' in query:
        params['output'] = query['output']
    for item in client.post('item.get', params):
        # there are some template items that we should skip
        if item['hostid'] not in hosts:
            continue
        item['host'] = hosts[item['hostid']]['name']
        items_[item['itemid']] = item
    sdc.log.debug('fetch_items_data() took ' + str(time.time() - start) + ' seconds')
    return items_


def group_ids_by_value_types(itemids_value_types):
    itemids_by_value_types = {}
    for item in itemids_value_types:
        if item['value_type'] not in itemids_by_value_types:
            itemids_by_value_types[item['value_type']] = []
        itemids_by_value_types[item['value_type']].append(item['itemid'])
    return itemids_by_value_types


def extract_item_ids(itemids_value_types_):
    return list(map(
        lambda x: x['itemid'],
        itemids_value_types_
    ))


def replace_item_macros(items_):
    host_ids_to_fetch_macros, itemids_with_macros = get_host_ids_to_fetch_macros(items_)
    res = client.post(
        'usermacro.get',
        {
            'output': ['hostid', 'macro', 'value'],
            'hostids': host_ids_to_fetch_macros,
        }
    )
    # macros look like
    # {
    #     'hostid1': {'{%MACRO1}': 'value1', '{%MACRO2}': 'value2'}
    # }
    macros = {}
    for macro in res:
        if macro['hostid'] not in macros:
            macros[macro['hostid']] = {}
        macros[macro['hostid']][macro['macro']] = macro['value']
    for itemid in itemids_with_macros:
        item = items_[itemid]
        for k, v in item.items():
            if isinstance(v, unicode) and re.search('({\$.*})', v):
                for macro_name in list(re.findall('({\$[^\}]+})', v)):
                    if macro_name in macros.get(item['hostid'], {}):
                        v = v.replace(macro_name, macros[item['hostid']][macro_name])
                item[k] = v
    return items_


def get_host_ids_to_fetch_macros(items_):
    itemids_with_macros = []
    host_ids_to_fetch_macros = []
    for item in items_.values():
        for k, v in item.items():
            if isinstance(v, unicode) and re.search('.*({\$.*})', v):
                host_ids_to_fetch_macros.append(item['hostid'])
                itemids_with_macros.append(item['itemid'])
                continue
    return host_ids_to_fetch_macros, itemids_with_macros


def main():
    end = get_backfill_offset() + get_interval()
    sdc.log.info('INTERVAL: ' + str(get_interval()))
    sdc.log.info('TIME_TO: ' + str(end))

    while True:
        try:
            if sdc.isStopped():
                break

            while end > get_now_with_delay():
                time.sleep(2)
                if sdc.isStopped():
                    return

            # they are ordered by itemid asc
            for itemids_value_types in chunks(fetch_itemids_value_types(end), int(sdc.userParams['ITEMS_BATCH_SIZE'])):
                batch = sdc.createBatch()
                itemids = extract_item_ids(itemids_value_types)
                items = fetch_items_data(itemids)
                items = replace_item_macros(items)

                for value_type, ids in group_ids_by_value_types(itemids_value_types).items():
                    for histories in query_history(ids, value_type, end):
                        for history in histories:
                            history.update(items[history['itemid']])
                            record = sdc.createRecord('record created ' + str(get_now_with_delay()))
                            record.value = history
                            batch.add(record)

                            if batch.size() == sdc.batchSize:
                                batch.process(entityName, str(end) + '_' + itemids[-1])
                                batch = sdc.createBatch()
                                if sdc.isPreview() and sdc.isStopped():
                                    break

                        if sdc.isStopped():
                            break

                # always process batch so that in case when there were no data, we save last processed itemid anyway
                batch.process(entityName, str(end) + '_' + itemids[-1])
                if sdc.isStopped():
                    break

            end += get_interval()
        except Exception:
            sdc.log.error(traceback.format_exc())
            raise


main()
