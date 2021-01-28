import re

from agent import cli, source, destination, pipeline, streamsets, di
from agent.modules import db, zabbix

di.init()

# cli.source.create()
# cli.destination()
# cli.pipeline.create()
# cli.streamsets.delete(["asdfa"])

c = zabbix.Client('http://localhost:8888', 'Admin', 'zabbix')
t = 1
