import rrdtool

from agent import cli, source, destination, pipeline, streamsets, di
from agent.modules import db
from agent.source import rrd

di.init()

rrd_file_path = '/Users/antonzelenin/Workspace/daria/agent/src/agent/data.rrd'
# info = rrdtool.info(rrd_file_path)

# r = rrdtool.fetch(rrd_file_path, 'LAST', ['-s', '1614865638', '-e', '1614866638', '-r', '300'])

# last_update = 1612801804
last_update = 1614866638
step = 300

period = 1000

start1 = last_update - period * 2
start2 = last_update - period

res = rrd.extract_metrics(
    source.repository.get_by_name('c'), str(start1), str(start1 + period), str(step),
    exclude_datasources=[], exclude_hosts=[]
)
t = 1
# res = [v['timestamp'] for v in res]
#
# res1 = rrd.extract_metrics(
#     source.repository.get_by_name('c'), str(start1), str(start1 + period), str(step),
#     exclude_datasources=[], exclude_hosts=[]
# )
# res1 = [v['timestamp'] for v in res1]
# res2 = rrd.extract_metrics(
#     source.repository.get_by_name('c'), str(start2), str(start2 + period), str(step),
#     exclude_datasources=[], exclude_hosts=[]
# )
# res2 = [v['timestamp'] for v in res2]

# cli.source.edit(["test_mongo"])
# cli.destination()
# cli.pipeline.create()
# cli.streamsets.delete(["asdfa"])
