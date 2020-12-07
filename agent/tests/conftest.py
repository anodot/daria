import json
import os
import pytest

from agent import di
from agent.api import main
from click.testing import CliRunner
from agent.modules import db

DUMMY_DESTINATION_OUTPUT_PATH = '/output'
TEST_DATASETS_PATH = '/home'


di.init()


class MyRunner(CliRunner):
    def invoke(self, *args, **kwargs):
        try:
            result = super(MyRunner, self).invoke(*args, **kwargs)
            db.session().commit()
            return result
        except Exception:
            db.session().rollback()
            raise
        finally:
            db.close_session()


@pytest.fixture(scope="session")
def cli_runner():
    yield MyRunner()


@pytest.fixture
def api_client():
    main.app.testing = True
    with main.app.test_client() as client:
        yield client


def get_output(file_name):
    for filename in os.listdir(DUMMY_DESTINATION_OUTPUT_PATH):
        if filename == file_name:
            with open(os.path.join(DUMMY_DESTINATION_OUTPUT_PATH, filename)) as f:
                return json.load(f)


def get_input_file_path(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_pipelines', 'input_files', f'{name}')


def pytest_generate_tests(metafunc):
    # called once per each test function
    if metafunc.cls is None or not hasattr(metafunc.cls, 'params') or metafunc.function.__name__ not in metafunc.cls.params:
        return
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist])
