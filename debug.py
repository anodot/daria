from agent import cli, source, destination, pipeline, streamsets, di
from agent.api import main
from agent.destination.anodot_api_client import AnodotApiClient
from agent.modules import db


def api_client():
    main.app.testing = True
    with main.app.test_client() as client:
        di.init()
        return client


di.init()

# res = api_client().get('/alerts?status=CLOSE&startTime=1623321686')
res = api_client().get('/alert/status?alertName=Drop%20in%20Device_uptime%20for%20All%20equipments&host=eNodeBbaicells180&startTime=-300')
t = 1

# cli.source.edit(["test_mongo"])
# cli.destination()
# cli.pipeline.create()
# cli.streamsets.delete(["asdfa"])
