from agent import cli, source, destination, pipeline, streamsets
from agent.modules import db

# cli.source.edit(["test_mongo"])
# cli.destination()
# cli.pipeline.create()
# cli.streamsets.delete(["asdfa"])

db.session().commit()
db.session().close()
