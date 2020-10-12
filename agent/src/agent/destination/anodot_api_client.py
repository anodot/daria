import requests
import urllib.parse
import click

from agent.destination import HttpDestination, AuthenticationToken
from agent.modules import proxy
from agent.modules.logger import get_logger
from agent import destination

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
    def __init__(self, destination_: HttpDestination):
        self.destination = destination_
        self.session = requests.Session()
        self._update_session_authorization()

    @property
    def url(self):
        return self.destination.url

    @property
    def proxies(self):
        return proxy.get_config(self.destination.proxy)

    def _update_session_authorization(self):
        if not self.destination.auth_token:
            self.destination.auth_token = \
                AuthenticationToken(self.destination, self._retrieve_new_token(self.destination))
            destination.repository.save_auth_token(self.destination.auth_token)
        elif self.destination.auth_token.is_expired():
            self.destination.auth_token.update(self._retrieve_new_token(self.destination))
            destination.repository.save_auth_token(self.destination.auth_token)
        self.session.headers.update({'Authorization': 'Bearer ' + self.destination.auth_token.authentication_token})

    def _retrieve_new_token(self, destination_: HttpDestination):
        response = requests.post(self._build_url('access-token'), json={'refreshToken': destination_.access_key},
                                 proxies=self.proxies)
        response.raise_for_status()
        return response.text.replace('"', '')

    def _build_url(self, *args) -> str:
        return urllib.parse.urljoin(self.url, '/'.join(['/api/v2', *args]))

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
    def send_pipeline_data_to_bc(self, pipeline_data: dict):
        self._update_session_authorization()
        return self.session.post(self._build_url('bc', 'agents'), proxies=self.proxies, json=pipeline_data)
