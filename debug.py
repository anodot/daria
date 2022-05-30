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

# dest = destination.repository.get()
#
# client = AnodotApiClient(dest)
# res = client.get_schemas()

# s = requests.Session()
# added this token on 19 may 17:26, wait until it's expired and try to send a request
# auth_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiMDgwNjVlYjA3ZTI4ZTRiZGVlZjkxZGJlNGZlOGU2ZWEwMjZlNzE4MzU2MzFjODIyYjEwNWMwMDI4ZWRlNGZlNjRjOGQ3NGIxODMxZmJkN2VmYmJiZmUwZGVlMmExMzQ0N2M3MmM2YzQyMjFiY2UzMjMwOGVhMDVkNjdkZjhkNjBiYjA0Mjg1Yjg3NGI3MTRlNTgiLCJpYXQiOjE2NTI5Njk5NTEsImV4cCI6MTY1NTU2MTk1MX0.Xbo4MyumlqUxWbFp_efQ4rSNrAqulL77pKT2JjWfRok'
# s.headers.update({
#     'Content-Type': 'application/json',
#     'Authorization': 'Bearer ' + auth_token
# })
#
# schemas = s.get(
#     'https://app.anodot.com/api/v2/stream-schemas/schemas'
# )
# t = 1
# load = s.post(
#     'https://app.anodot.com/api/v2/topology/map/load/start'
# )
# t = 1
# row = {
#     "address": "5th Ave, 122",
#     "parent_region_dimension_id": "Battambang",
#     "longitude": 100.01,
#     "type": "Mobile RAN",
#     "domain": "RAN",
#     "name": "BB001",
#     "id": "BB001",
#     "latitude": 10.005
# }
# s_row = json.dumps(row)
# rows = {
#     "BB001": s_row
# }
# s_rows = {"BB001": "{\"address\": \"5th Ave, 122\",\"parent_region_dimension_id\": \"Battambang\",\"longitude\": 100.01,\"type\": \"Mobile RAN\",\"domain\": \"RAN\",\"name\": \"BB001\",\"id\": \"BB001\",\"latitude\": 10.005}"}
#
# data = {
#     "bulkSerNumber": 1,
#     "type": "SITE",
#     "rows": rows,
#     "numberOfRows": 1,
#     "rollupId": 49
# }
#
# res = s.put(
#     'https://app.anodot.com/api/v2/topology/map/load/49',
#     json=data
# )
# t = 1
#
# res = s.put(
#     'https://app.anodot.com/api/v2/topology/user',
#     json={
#         '_id': '5e819f0bd7a1e5000de34385'
#     }
# )

# res = api_client().get('/alerts?status=CLOSE&startTime=1623321686')
# res = api_client().get('/alert/status?alertName=Drop%20in%20Device_uptime%20for%20All%20equipments&host=eNodeBbaicells180&startTime=-300')

# s = http.Session()
# r = s.get('https://10.237.70.2:17778/SolarWinds/InformationService/v3/Json/Query?query=select+top+1+1+as+test+from+Orion.Accounts')
# r.raise_for_status()
# r = snmp.extract_metrics(pipeline.repository.get_by_id('snmp'))

# res = data_extractor.observium.extract_metrics(pipeline.repository.get_by_id('observium_storage_transform'), 1652979622)
# cli.pipeline.create(["-f", "/Users/antonzelenin/Workspace/daria/agent/tests/input_files/promql/pipelines.json"])
# cli.destination()
# cli.pipeline.create()
# cli.streamsets.delete(["asdfa"])
t = 1
