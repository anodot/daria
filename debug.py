import re

from agent import cli, source, destination, pipeline, streamsets
from agent.modules import db

# cli.source.edit(["test_mongo"])
# cli.destination()
cli.pipeline.edit(["-a", "test_transform_value"])
# cli.streamsets.delete(["asdfa"])
