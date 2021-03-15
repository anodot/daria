import json
import random
import rrdtool

# rrd_file_path = 'agent/tests/input_files/data2.rrd'
rrd_file_path = 'test.rrd'
# info = rrdtool.info(rrd_file_path)
# r = rrdtool.fetch(rrd_file_path, 'AVERAGE', ['-s', '1615766700', '-r', '300'])
# t = 1
# values = []
# start = 1615766400
# step = 300
# for i in range(1, 10):
#     values.append(f"{start + step * i}:{random.randint(0, 9)}")
#
# args = ["test.rrd"] + values
#
# rrdtool.update(args)

from agent import cli, source, destination, pipeline, streamsets, di
from agent.api import main
from agent.modules import db, zabbix
from datetime import datetime, timedelta

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
# r = rrdtool.fetch(rrd_file_path, 'AVERAGE', ['-s', '1614988800', '-r', '300'])
# r = rrdtool.fetch(rrd_file_path, 'AVERAGE', ['-s', '1615808125', '-r', '300'])
#
# with open('agent/output/cacti_cacti.json', 'r') as f:
#     actual = json.load(f)
#
#
# def trans(dd):
#     new = {}
#     for obj in dd:
#         times = obj['timestamp']
#         if times not in new:
#             new[times] = []
#         new[times].append(obj['value'])
#     return new
#
#
# actual = trans(actual)
#
# expected = []
# with open('agent/tests/test_pipelines/expected_output/data1_rrd.json', 'r') as f:
#     expected.extend(json.load(f))
#
#
# def trans_expected(dd):
#     new = {}
#     for obj in dd:
#         times = obj['timestamp']
#         if times not in new:
#             new[times] = []
#         new[times].append(obj['0'])
#         new[times].append(obj['1'])
#         if '2' in obj:
#             new[times].append(obj['2'])
#     return new
#
#
# expected = trans_expected(expected)
#
# assert expected == actual
#
# print('hoorrayy')
# exit()


di.init()


def api_client():
    main.app.testing = True
    with main.app.test_client() as client:
        di.init()
        return client


for i in range(0, 5):
    start = 1615766700
    r = api_client().get(f'/rrd_source/fetch_data/cacti_file?step=300&start={start + 300 * i}&end={start + 300 + 300 * i}').json
    t = 1

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

cli.pipeline.create(["-f", "/Users/antonzelenin/Workspace/daria/agent/tests/input_files/cacti_pipelines.json"])
# cli.destination()
# cli.pipeline.create()
# cli.streamsets.delete(["asdfa"])
