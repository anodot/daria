import pytest
from agent.api import main


@pytest.fixture
def client():
    main.app.testing = True
    with main.app.test_client() as client:
        yield client
