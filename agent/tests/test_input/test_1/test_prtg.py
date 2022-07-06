from ..test_zpipeline_base import TestInputBase


class TestPrtg(TestInputBase):
    __test__ = True
    params = {
        'test_create_source_with_file': [{
            'file_name': 'prtg/sources'
        }],
        'test_create_with_file': [{
            'file_name': 'prtg/pipelines'
        }],
    }

    def test_create_source_with_file(self, cli_runner, file_name):
        super().test_create_source_with_file(cli_runner, file_name)

    def test_create_with_file(self, cli_runner, file_name, override_config):
        super().test_create_with_file(cli_runner, file_name, override_config)
