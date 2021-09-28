from datetime import datetime
from .base import InputBaseTest
from ..conftest import generate_input
from agent import cli, source, pipeline


class TestSolarwinds(InputBaseTest):
    params = {
        'test_create_source_with_file': [{'file_name': 'solarwinds_sources'}],
        'test_create_with_file': [{'file_name': 'solarwinds_pipelines'}],
    }

    def test_source_create(self, cli_runner):
        source_name = 'solarwinds'
        input_ = {
            'type': 'solarwinds',
            'name': source_name,
            'api url': 'http://dummy_destination:80/',
            'api user': 'Admin',
            'api pass': 'admin',
        }
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        assert source.repository.exists(source_name)

    def test_pipeline_create(self, cli_runner):
        offset = datetime.fromtimestamp(1617062400)
        pipeline_id = 'solarwinds'
        input_ = {
            'source': 'solarwinds',
            'id': pipeline_id,
            'query': 'SELECT TOP 1000 NodeID, DateTime, Archive, MinLoad, MaxLoad, AvgLoad, TotalMemory,'
                     ' MinMemoryUsed, MaxMemoryUsed, AvgMemoryUsed, AvgPercentMemoryUsed'
                     ' FROM Orion.CPULoad WHERE {TIMESTAMP_CONDITION}',
            'delay': 0,
            'collect since': (datetime.now() - offset).days,
            'interval in sec': 86400,
            'timestamp property name': 'DateTime',
            'timestamp type': 'string',
            'timestamp format': "yyyy-MM-dd'T'HH:mm:ss",
            'count': 'n',
            'metrics': 'MinMemoryUsed:gauge AvgPercentMemoryUsed:gauge',
            'metric names': 'MinMemoryUsed:MinMemoryUsed AvgPercentMemoryUsed:AvgPercentMemoryUsed',
            'req dimensions': 'NodeID',
            'optional dimensions': '',
            'preview': 'y',
        }
        result = cli_runner.invoke(cli.pipeline.create, catch_exceptions=False, input=generate_input(input_))
        assert result.exit_code == 0
        pipeline.repository.get_by_id(pipeline_id)
