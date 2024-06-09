import traceback
import pytest

from ..test_zpipeline_base import TestInputBase
from ...conftest import get_input_file_path, Order
from agent import source, cli


class TestTCPServer(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{'file_name': 'tcp_sources'}],
        'test_create_with_file': [{'file_name': 'tcp_pipelines'}],
    }

    @pytest.mark.order(Order.PIPELINE_CREATE)
    def test_create(self, cli_runner):
        pipeline_id = 'test_tcp_log'
        result = cli_runner.invoke(cli.pipeline.create, catch_exceptions=False,
                                   input=f"test_tcp_log\n{pipeline_id}\n\nn\nClicks:gauge\nClicks:clicks\ntimestamp_unix_ms\nunix_ms\nver Country\nExchange optional_dim\n\n")
        assert result.exit_code == 0
