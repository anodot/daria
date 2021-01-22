import requests
from sqlalchemy import create_engine


def post(method, auth, params):
    res = requests.post('http://zabbix-web:8080/api_jsonrpc.php', json={
        'jsonrpc': '2.0',
        'method': method,
        'params': params,
        'id': 1,
        'auth': auth
    })
    res.raise_for_status()
    result = res.json()
    if 'error' in result:
        raise Exception(str(result))

    return result['result']


HOSTNAME = 'zabbixagent'

auth_token = post('user.login', None, {'user': 'Admin', 'password': 'zabbix'})
print('Auth successful')
host = post('host.create', auth_token, {
    'host': HOSTNAME,
    'groups': [{'groupid': 4}],
    'interfaces': [{'type': 1, 'main': 1, 'dns': HOSTNAME, 'useip': 0, 'ip': '', 'port': 10500}]
})
host_id = host['hostids'][0]
print('Host created')

interface = post('hostinterface.get', auth_token, {
    'hostids': host_id
})
interface_id = interface[0]['interfaceid']

cpu_item = post('item.create', auth_token, {
    'hostid': host_id,
    'name': 'CPU',
    'key_': 'system.cpu.load',
    'type': 0,
    'value_type': 0,
    'delay': '30s',
    'interfaceid': interface_id
})
cpu_item_id = cpu_item['itemids'][0]
print('CPU item created')

memory_item = post('item.create', auth_token, {
    'hostid': host_id,
    'name': 'Memory',
    'key_': 'vm.memory.size',
    'type': 0,
    'value_type': 3,
    'delay': '30s',
    'interfaceid': interface_id
})
memory_item_id = memory_item['itemids'][0]
print('Memory item created')

cpu_values = [
    (cpu_item_id, '1611322479', '0.1', '257117700'),
    (cpu_item_id, '1611322529', '0.23', '267117877'),
    (cpu_item_id, '1611322559', '0.15', '267237777')
]
memory_values = [
    (memory_item_id, '1611322470', '10000567', '257136700'),
    (memory_item_id, '1611322520', '9347567', '267187877'),
    (memory_item_id, '1611322550', '9347293', '267239977')
]

values = ','.join(map(lambda x: '(' + ','.join(x) + ')', cpu_values + memory_values))
mysql_conn = create_engine(f'mysql+mysqlconnector://root@mysql/zabbix')
mysql_conn.execute(f'INSERT INTO history (itemid, clock, value, ns) VALUES {values};')
print('history inserted')
