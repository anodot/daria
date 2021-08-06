import requests

from agent.data_extractor.snmp import snmp
from agent import cli, source, destination, pipeline, streamsets, di
from agent.api import main
from agent.destination.anodot_api_client import AnodotApiClient
from agent.modules import db, http


def api_client():
    main.app.testing = True
    with main.app.test_client() as client:
        di.init()
        return client


di.init()


cli.pipeline.edit(["i"])


exit()


# def _filter(l):
#     return list(filter(lambda x: bool(x), l))
#
#
# def csv_to_dict(csv_data):
#     results = _filter(csv_data.split('\r\n\r\n'))
#     data = []
#     for result in results:
#         rows = result.split('\r\n')
#         header = _filter(rows.pop(0).split(','))
#         for row in rows:
#             data.append(dict(
#                 zip(header, _filter(row.split(',')))
#             ))
#     return data


session = requests.Session()
# todo take token from pipeline
session.headers['Authorization'] = 'Token token'
session.headers['Content-type'] = 'application/vnd.flux'
session.headers['Accept'] = 'application/json'
res = session.post(
    'http://localhost:8087/api/v2/query?org=test',
    data='from(bucket:"test") |> range(start: 1552654426, stop: 1553154426) |> filter(fn: (r) => r._measurement == "cpu_test")'
    # внизу рендж из пайплайна и в него данные почему-то не попадают, нужно брать больше 120 тыщ сек чтоб данные были
    # data='from(bucket:"test") |> range(start:  1552222380, stop: 1552342380) |> filter(fn: (r) => r._measurement == "cpu_test")'
)
res.raise_for_status()
data = csv_to_dict(res.text)

t = 1


# res = api_client().get('/alerts?status=CLOSE&startTime=1623321686')
# res = api_client().get('/alert/status?alertName=Drop%20in%20Device_uptime%20for%20All%20equipments&host=eNodeBbaicells180&startTime=-300')


# s = http.Session()
# r = s.get('https://10.237.70.2:17778/SolarWinds/InformationService/v3/Json/Query?query=select+top+1+1+as+test+from+Orion.Accounts')
# r.raise_for_status()
# r = snmp.extract_metrics(pipeline.repository.get_by_id('snmp'))

t = 1

# cli.source.edit(["solarwinds"])
# cli.destination()
cli.pipeline.create()
# cli.streamsets.delete(["asdfa"])
