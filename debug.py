from agent import cli, source, destination, pipeline, streamsets, di
from agent.modules import db
from agent.source import rrd

di.init()

rrd.extract_metrics(source.repository.get_by_name('c'), '1612791804', '1612801804', '300',
                    exclude_datasources=['test'], exclude_hosts=[])

# import rrdtool
#
# file = '/Users/antonzelenin/Workspace/daria/agent/src/agent/data.rrd'
#
# AVERAGE = "AVERAGE"
# MIN = "MIN"
# MAX = "MAX"
# LAST = "LAST"
#
# info = rrdtool.info(file)
# r = rrdtool.fetch(file, AVERAGE, ['-s', '1611999000', '-e', '1612710000', '-r', '5'])
# t = 1

# cli.source.edit(["test_mongo"])
# cli.destination()
# cli.pipeline.create()
# cli.streamsets.delete(["asdfa"])
