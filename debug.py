import json
import os

import rrdtool

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


# i = rrdtool.info('/Users/antonzelenin/Workspace/daria/smart2.rrd')
# res = rrdtool.fetch(
#     '/Users/antonzelenin/Workspace/daria/agent/tests/input_files/rrd/1/cacti.rrd',
    # '/Users/antonzelenin/Workspace/daria/smart2.rrd',
    # 'AVERAGE',
    # ['-s', '1619085000', '-e', '1619095000', '-r', '300']
    # ['-s', '1644469345', '-e', '1644570345', '-r', '300']
# )


di.init()
# res = api_client().get('/alerts?status=CLOSE&startTime=1623321686')
# res = api_client().get('/alert/status?alertName=Drop%20in%20Device_uptime%20for%20All%20equipments&host=eNodeBbaicells180&startTime=-300')

# s = http.Session()
# r = s.get('https://10.237.70.2:17778/SolarWinds/InformationService/v3/Json/Query?query=select+top+1+1+as+test+from+Orion.Accounts')
# r.raise_for_status()
# r = snmp.extract_metrics(pipeline.repository.get_by_id('snmp'))

t = 1

res = data_extractor.rrd.extract_metrics(pipeline.repository.get_by_id('rrd'), '1619085000',  '1619086800', '300')
# cli.pipeline.create(["-f", "/Users/antonzelenin/Workspace/daria/agent/tests/input_files/rrd/pipelines.json"])
# cli.destination()
# cli.pipeline.create()
# cli.streamsets.delete(["asdfa"])
t = 1
