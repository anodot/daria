import requests
import urllib.parse
import click

from agent.modules import proxy
from agent.modules.logger import get_logger
from agent import pipeline, source, destination

logger = get_logger(__name__)


def endpoint(func):
    """
    Decorator for api endpoints. Logs errors and returns json response

    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        try:
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError:
            if res.text:
                logger.error(res.text)
            raise

    return wrapper


class AnodotApiClientException(click.ClickException):
    pass


class AnodotApiClient:
    def __init__(self, access_key, proxies, base_url='https://app.anodot.com'):
        self.access_key = access_key
        self.base_url = base_url
        self.proxies = proxies
        self.session = requests.Session()
        self._get_auth_token()

    def _get_auth_token(self):
        auth_token = self.session.post(self._build_url('access-token'),
                                       json={'refreshToken': self.access_key},
                                       proxies=self.proxies)
        auth_token.raise_for_status()
        self.session.headers.update({'Authorization': 'Bearer ' + auth_token.text.replace('"', '')})

    def _build_url(self, *args) -> str:
        return urllib.parse.urljoin(self.base_url, '/'.join(['/api/v2', *args]))

    @endpoint
    def create_schema(self, schema):
        return self.session.post(self._build_url('stream-schemas'), json=schema, proxies=self.proxies)

    @endpoint
    def delete_schema(self, schema_id):
        return self.session.delete(self._build_url('stream-schemas', schema_id), proxies=self.proxies)

    @endpoint
    def send_topology_data(self, data_type, data):
        return self.session.post(self._build_url('topology', 'data'), proxies=self.proxies,
                                 data=data, params={'type': data_type})

    @endpoint
    def send_source_to_bc(self, source_: source.Source):
        pass
        # return self.session.post(self._build_url('todo-source'), proxies=self.proxies, json=source_.to_dict())

    @endpoint
    def send_pipeline_to_bc(self, pipeline_: pipeline.Pipeline):
        pass
        # return self.session.post(self._build_url('todo-pipeline'), proxies=self.proxies, json=pipeline_.to_dict())


def get_client(destination_: destination.HttpDestination = None) -> AnodotApiClient:
    if not destination_:
        destination_ = destination.repository.get()
    return AnodotApiClient(destination_.access_key, proxy.get_config(destination_.proxy), destination_.url)
