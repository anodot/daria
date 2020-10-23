from agent import cli, source, destination

# help('modules')

# cli.source.edit(["test_mongo"])
# cli.destination()
# cli.pipeline.create()
# cli.update()
from agent.modules import streamsets
from agent.pipeline import Pipeline
from agent.source import Source

p = Pipeline(
    'test',
    source.repository.get_last_edited('influx'),
    destination.repository.get(),
    streamsets.repository.get(1)
)
