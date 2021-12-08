import requests
import urllib.parse
import click

from typing import Optional
from agent.destination import HttpDestination, AuthenticationToken
from agent.modules import proxy
from agent.modules.logger import get_logger
from agent import destination

logger = get_logger(__name__)


def endpoint(func):
    """
    Logs errors and returns json response
    """
    def wrapper(*args, **kwargs):
        args[0].refresh_session_authorization()
        res = func(*args, **kwargs)
        try:
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError:
            if res.text:
                message = f'{res.url} - {res.text}'
                logger.error(message)
                raise Exception(message)
            raise

    return wrapper


class AnodotApiClientException(click.ClickException):
    pass


class AnodotApiClient:
    def __init__(self, destination_: HttpDestination):
        self.url = destination_.url
        self.access_key = destination_.access_key
        self.proxies = proxy.get_config(destination_.proxy)
        self.session = requests.Session()
        self.auth_token: Optional[AuthenticationToken] = destination_.auth_token
        if self.auth_token:
            self.session.headers.update({'Authorization': 'Bearer ' + self.auth_token.authentication_token})

    def refresh_session_authorization(self):
        if self.auth_token and self.auth_token.is_expired():
            self.auth_token.update(self.get_new_token())
            destination.repository.save_auth_token(self.auth_token)
            self.session.headers.update({'Authorization': 'Bearer ' + self.auth_token.authentication_token})

    def get_new_token(self):
        response = requests.post(
            self._build_url('access-token'), json={'refreshToken': self.access_key}, proxies=self.proxies
        )
        response.raise_for_status()
        return response.text.replace('"', '')

    def _build_url(self, *args) -> str:
        return urllib.parse.urljoin(self.url, '/'.join(['/api/v2', *args]))

    @endpoint
    def create_schema(self, schema):
        return self.session.post(self._build_url('stream-schemas'), json=schema, proxies=self.proxies)

    def _delete_schema_old_api(self, schema_id):
        """
        Used for old anodot api version (for on-prem)
        :param schema_id:
        :return:
        """
        return self.session.delete(self._build_url('stream-schemas', schema_id), proxies=self.proxies)

    @endpoint
    def delete_schema(self, schema_id):
        try:
            res = self.session.delete(self._build_url('stream-schemas', 'schemas', schema_id), proxies=self.proxies)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return self._delete_schema_old_api(schema_id)
            raise

    @endpoint
    def send_topology_data(self, data_type, data):
        return self.session.post(
            self._build_url('topology', 'data'), proxies=self.proxies, data=data, params={'type': data_type}
        )

    @endpoint
    def send_pipeline_data_to_bc(self, pipeline_data: dict):
        return self.session.post(self._build_url('bc', 'agents'), proxies=self.proxies, json=pipeline_data)

    @endpoint
    def delete_pipeline_from_bc(self, pipeline_id: str):
        return self.session.delete(
            self._build_url('bc', 'agents'),
            proxies=self.proxies,
            params={'pipelineId': pipeline_id},
        )

    def _get_schemas_old_api(self):
        """
        Used for old anodot api version (for on-prem)
        :return:
        """
        return self.session.get(self._build_url('stream-schemas'), params={'excludeCubes': True}, proxies=self.proxies)

    @endpoint
    def get_schemas(self):
        try:
            res = self.session.get(
                self._build_url('stream-schemas', 'schemas'),
                params={'excludeCubes': True},
                proxies=self.proxies,
            )
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return self._get_schemas_old_api()
            raise

    @endpoint
    def get_alerts(self, params: dict):
        return self.session.get(
            self._build_url('alerts', 'triggered'),
            params=params,
            proxies=self.proxies,
        )
