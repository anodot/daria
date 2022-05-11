import requests

from requests.auth import HTTPBasicAuth
from agent.modules.data_source import DataSource

BASIC_AUTH = 'basic'


class API(DataSource):
    def __init__(self, url: str, auth_config: dict):
        self.url: str = url
        # self.url = 'http://localhost:8080/api/v1/site'
        self.authentication = _get_authentication(auth_config)

    def get_data(self) -> list[dict]:
        res = requests.get(self.url, auth=self.authentication)
        res.raise_for_status()
        return res.json()


def _get_authentication(config: dict):
    type_ = config['type']
    if type_ == BASIC_AUTH:
        return HTTPBasicAuth(config['username'], config['password'])
    else:
        raise Exception(f'Invalid authentication type provided: `{type_}`')
