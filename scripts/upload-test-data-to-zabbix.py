from sqlalchemy import create_engine
from agent.modules import zabbix


HOSTNAME = 'zabbixagentґ'

client = zabbix.Client('http://zabbix-web:8080', 'Admin', 'zabbix')
print('Auth successful')

host = client.post('host.create', {
    'host': HOSTNAME,
    'groups': [{'groupid': 4}],
    'interfaces': [{'type': 1, 'main': 1, 'dns': HOSTNAME, 'useip': 0, 'ip': '', 'port': 10500}]
})
host_id = host['hostids'][0]
print('Host created')

interface = client.post('hostinterface.get', {
    'hostids': host_id
})
interface_id = interface[0]['interfaceid']

cpu_item = client.post('item.create', {
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

memory_item = client.post('item.create', {
    'hostid': host_id,
    'name': 'agent - Memory - anodot',
    'key_': 'vm.memory.size[{$MY_MACRO},{$MY_MACRO_2}]',
    'type': 0,
    'value_type': 3,
    'delay': '30s',
    'interfaceid': interface_id
})
memory_item_id = memory_item['itemids'][0]
print('Memory item created')

client.post('usermacro.create', {
    "hostid": host_id,
    "macro": "{$MY_MACRO}",
    "value": "macro_value"
})
print('Macro MY_MACRO created')

client.post('usermacro.create', {
    "hostid": host_id,
    "macro": "{$MY_MACRO_2}",
    "value": "macro_value_2"
})
print('Macro MY_MACRO_2 created')

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

cpu_values = ','.join(map(lambda x: '(' + ','.join(x) + ')', cpu_values))
memory_values = ','.join(map(lambda x: '(' + ','.join(x) + ')', memory_values))

mysql_conn = create_engine('mysql+mysqlconnector://root@mysql/zabbix')
mysql_conn.execute(f'INSERT INTO history (itemid, clock, value, ns) VALUES {cpu_values};')
mysql_conn.execute(f'INSERT INTO history_uint (itemid, clock, value, ns) VALUES {memory_values};')
print('history inserted')
