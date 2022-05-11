import json

import requests

from agent.data_extractor.snmp import snmp
from agent import cli, source, destination, pipeline, streamsets, di, data_extractor
from agent.api import main
from agent.destination.anodot_api_client import AnodotApiClient
from agent.modules import db, http


def api_client():
    main.app.testing = True
    with main.app.test_client() as client:
        di.init()
        return client


di.init()

dest = destination.repository.get()

client = AnodotApiClient(dest)
res = client.get_schemas()

s = requests.Session()
s.headers.update({
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + dest.auth_token.authentication_token
})

schemas = s.get(
    'https://app.anodot.com/api/v2/stream-schemas/schemas'
)

load = s.post(
    'https://app.anodot.com/api/v2/topology/map/load/start'
)
t = 1

# res = s.put(
#     'https://app.anodot.com/api/v2/topology/user',
#     json={
#         '_id': '5e819f0bd7a1e5000de34385'
#     }
# )
# t = 1
exit()

# res = api_client().get('/alerts?status=CLOSE&startTime=1623321686')
# res = api_client().get('/alert/status?alertName=Drop%20in%20Device_uptime%20for%20All%20equipments&host=eNodeBbaicells180&startTime=-300')

# s = http.Session()
# r = s.get('https://10.237.70.2:17778/SolarWinds/InformationService/v3/Json/Query?query=select+top+1+1+as+test+from+Orion.Accounts')
# r.raise_for_status()
# r = snmp.extract_metrics(pipeline.repository.get_by_id('snmp'))

res = data_extractor.topology.extract_metrics(pipeline.repository.get_by_id('topology'))
# cli.pipeline.create(["-f", "/Users/antonzelenin/Workspace/daria/agent/tests/input_files/promql/pipelines.json"])
# cli.destination()
# cli.pipeline.create()
# cli.streamsets.delete(["asdfa"])
t = 1
