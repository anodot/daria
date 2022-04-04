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


di.init()

# res = data_extractor.rrd.extract_metrics(pipeline.repository.get_by_id('rrd'), '1619085000',  '1619086800', '300')
# cli.pipeline.create(["-f", "/Users/antonzelenin/Workspace/daria/agent/tests/input_files/rrd/pipelines.json"])
# cli.destination()
# cli.pipeline.create(['-f', '/Users/antonzelenin/Workspace/daria/agent/tests/input_files/directory/pipelines.json'])
# cli.streamsets.delete(["asdfa"])
t = 1
