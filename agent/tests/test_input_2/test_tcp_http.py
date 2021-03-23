import traceback

from ..test_input.test_zpipeline_base import TestInputBase
from ..conftest import get_input_file_path
from agent import source, cli


class TestTCPServer(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'tcp_sources'}],
        'test_create_with_file': [{'file_name': 'tcp_pipelines'}],
    }

    def test_source_create(self, cli_runner):
        grok_file_path = get_input_file_path('grok_patterns.txt')
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False,
                                   input="splunk\ntest_tcp_log\n9999\nLOG\n" + grok_file_path + "\n%{NONNEGINT:timestamp_unix_ms} %{TIMESTAMP:timestamp_string} %{NONNEGINT:ver} %{WORD} %{WORD:Country} %{WORD:AdType} %{WORD:Exchange} %{NUMBER:Clicks}\n")
        traceback.print_exception(*result.exc_info)
        assert result.exit_code == 0
        assert source.repository.exists('test_tcp_log')

    def test_create(self, cli_runner):
        pipeline_id = 'test_tcp_log'
        result = cli_runner.invoke(cli.pipeline.create, catch_exceptions=False,
                                   input=f"test_tcp_log\n{pipeline_id}\n\nn\nClicks:gauge\nClicks:clicks\ntimestamp_unix_ms\nunix_ms\nver Country\nExchange optional_dim\n\n")
        assert result.exit_code == 0

    def test_create_with_file(self, cli_runner, file_name):
        super().test_create_with_file(cli_runner, file_name)

    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)
