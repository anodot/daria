from sqlalchemy import create_engine
from agent.modules import zabbix


HOSTNAME = 'zabbixagent6'
N_RECORDS = 1000

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

for j in range(0, 2):
    # cpu_item = client.post('item.create', {
    #     'hostid': host_id,
    #     'name': 'CPU',
    #     'key_': 'system.cpu.load' + str(j),
    #     'type': 0,
    #     'value_type': 0,
    #     'delay': '30s',
    #     'interfaceid': interface_id
    # })
    # cpu_item_id = cpu_item['itemids'][0]
    # print(str(j) + ' CPU item created')

    memory_item = client.post('item.create', {
        'hostid': host_id,
        'name': 'agent - Memory - anodot',
        'key_': 'vm.memory.size_aa' + str(j),
        'type': 0,
        'value_type': 3,
        'delay': '30s',
        'interfaceid': interface_id
    })
    memory_item_id = memory_item['itemids'][0]
    print(str(j) + ' Memory item created')


    cpu_values = []
    memory_values = []
    for i in range(0, N_RECORDS):
        # cpu_values.append((cpu_item_id, str(1611322479 + i), '0.1', '257117700'))
        # cpu_values.append((cpu_item_id, str(1611322529 + i), '0.23', '267117877'))
        # cpu_values.append((cpu_item_id, str(1611322559 + i), '0.15', '267237777'))

        memory_values.append((memory_item_id, str(1611322470 + i * 10), '10000567', '257136700'))
        # memory_values.append((memory_item_id, str(1611322520 + i), '9347567', '267187877'))
        # memory_values.append((memory_item_id, str(1611322550 + i), '9347293', '267239977'))

    # cpu_values = ','.join(map(lambda x: '(' + ','.join(x) + ')', cpu_values))
    memory_values = ','.join(map(lambda x: '(' + ','.join(x) + ')', memory_values))

    engine = create_engine(f'mysql+mysqlconnector://root@agent-mysql:3306/zabbix')
    with engine.connect() as mysql_conn:
        # mysql_conn.execute(f'INSERT INTO history (itemid, clock, value, ns) VALUES {cpu_values};')
        mysql_conn.execute(f'INSERT INTO history_uint (itemid, clock, value, ns) VALUES {memory_values};')
        mysql_conn.commit()

print('history inserted')
