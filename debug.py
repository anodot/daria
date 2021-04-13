from agent import cli, source, destination, pipeline, streamsets, di, data_extractor
from agent.modules import db
import rrdtool

di.init()

rrd_file_path = "/Users/antonzelenin/Workspace/daria/agent/tests/input_files/cacti.rrd"
# r = rrdtool.fetch(rrd_file_path, 'AVERAGE', ['-s', '1615766700', '-e', '1615767300', '-r', '300'])
i = rrdtool.info(rrd_file_path)
r = data_extractor.cacti.new_extract_metrics(pipeline.repository.get_by_id('cacti_dir'), '1615766100', '1615769100', '300')
t = 1

# cli.source.edit(["test_mongo"])
# cli.destination()
# cli.pipeline.create()
# cli.streamsets.delete(["asdfa"])
