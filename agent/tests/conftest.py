import json
import os
import pytest

from click.testing import CliRunner
from agent import di
from agent.api import main
from agent.modules import db

DUMMY_DESTINATION_OUTPUT_PATH = '/output'
TEST_DATASETS_PATH = '/home'

INPUT_FILES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_pipelines', 'input_files')


class MyRunner(CliRunner):
    def invoke(self, *args, **kwargs):
        try:
            di.init()
            result = super(MyRunner, self).invoke(*args, **kwargs)
            db.Session.commit()
            return result
        except Exception:
            db.Session.rollback()
            raise


@pytest.fixture(scope="session")
def cli_runner():
    yield MyRunner()


@pytest.fixture
def api_client():
    main.app.testing = True
    with main.app.test_client() as client:
        di.init()
        yield client


def get_output(file_name):
    for filename in os.listdir(DUMMY_DESTINATION_OUTPUT_PATH):
        if filename == file_name:
            with open(os.path.join(DUMMY_DESTINATION_OUTPUT_PATH, filename)) as f:
                return json.load(f)


def get_input_file_path(name):
    return os.path.join(INPUT_FILES_DIR, f'{name}')


def pytest_generate_tests(metafunc):
    # called once per each test function
    if metafunc.cls is None or not hasattr(metafunc.cls, 'params') or metafunc.function.__name__ not in metafunc.cls.params:
        return
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist])


def generate_input(input_: dict) -> str:
    return '\n'.join(map(
        lambda x: str(x),
        input_.values()
    ))
