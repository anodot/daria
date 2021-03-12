import json
import rrdtool

from agent import cli, source, destination, pipeline, streamsets, di
from agent.api import main
from agent.modules import db, zabbix
from datetime import datetime, timedelta

rrd_file_path = './agent/tests/input_files/data2.rrd'
info = rrdtool.info(rrd_file_path)
t = 1

# with open('/Users/antonzelenin/Workspace/daria/agent/output/cacti_cacti.json') as f:
#     new = {}
#     data = json.load(f)
#     for obj in data:
#         if obj['timestamp'] not in new:
#             new[obj['timestamp']] = []
#         new[obj['timestamp']].append(obj['value'])
#     with(open('blabla.json', 'a+')) as ff:
#         json.dump(new, ff)
#
#
# exit()

# todo this is how I checked expected output for tests, delete this and data1_rrd in case tests are ok
r = rrdtool.fetch(rrd_file_path, 'AVERAGE', ['-s', '1614988800', '-r', '300'])

with open('agent/output/cacti_cacti.json', 'r') as f:
    actual = json.load(f)


def trans(dd):
    new = {}
    for obj in dd:
        times = obj['timestamp']
        if times not in new:
            new[times] = []
        new[times].append(obj['value'])
    return new


actual = trans(actual)

expected = []
with open('agent/tests/test_pipelines/expected_output/data1_rrd.json', 'r') as f:
    expected.extend(json.load(f))


def trans_expected(dd):
    new = {}
    for obj in dd:
        times = obj['timestamp']
        if times not in new:
            new[times] = []
        new[times].append(obj['0'])
        new[times].append(obj['1'])
        if '2' in obj:
            new[times].append(obj['2'])
    return new


expected = trans_expected(expected)

assert expected == actual

print('hoorrayy')
exit()


# di.init()


# def api_client():
#     main.app.testing = True
#     with main.app.test_client() as client:
#         di.init()
#         return client


# r = api_client().get('/rrd_source/fetch_data/ca?step=300').json

# step = 300
# data_start = r[0][0]
# with open('agent/tests/test_pipelines/expected_output/data2_rrd.json', 'a+') as f:
#     for row_idx, data in enumerate(r[2]):
#         timestamp = int(data_start) + row_idx * int(step)
#         d = {'timestamp': timestamp, '0': data[0], '1': data[1], '2': data[2]}
#         json.dump(d, f)
#         f.write(',\n')
#
#
# exit()

# cli.source.edit(["test_mongo"])
# cli.destination()
# cli.pipeline.create()
# cli.streamsets.delete(["asdfa"])
