from agent import cli
from agent.pipeline import cli as pipeline_cli
from agent.destination import cli as destination_cli
from agent.source import cli as source_cli

# cli.destination()
# source_cli.create()
pipeline_cli.create(['-f', '/Users/antonzelenin/Workspace/daria/agent/tests/test_pipelines/input_files/elastic_pipelines.json']);
