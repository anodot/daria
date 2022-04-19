import requests
import urllib.parse
import click

from typing import Optional
from agent.destination import HttpDestination, AuthenticationToken
from agent.modules import proxy
from agent.modules.logger import get_logger
from agent import destination

logger = get_logger(__name__)


def process_response(res: requests.Response):
    """
    Logs errors and returns json response
    """
    try:
        res.raise_for_status()
        parsed = res.json()
    except requests.exceptions.HTTPError:
        if res.text:
            logger.error(f'{res.url} - {res.text}')
        elif res.json():
            logger.error(f'{res.url} - {res.json()}')
        raise

    return parsed


def v2endpoint(func):
    def wrapper(*args, **kwargs):
        args[0].refresh_session_authorization()
        return process_response(func(*args, **kwargs))

    return wrapper


def v1endpoint(func):
    def wrapper(*args, **kwargs):
        return process_response(func(*args, **kwargs))

    return wrapper


class AnodotApiClientException(click.ClickException):
    pass


class AnodotApiClient:
    def __init__(self, destination_: HttpDestination):
        self.url = destination_.url
        self.access_key = destination_.access_key
        self.api_token = destination_.token
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
            self.get_refresh_token_url(), json={'refreshToken': self.access_key}, proxies=self.proxies
        )
        response.raise_for_status()
        return response.text.replace('"', '')

    def _build_url(self, *args, api_version='v2') -> str:
        return urllib.parse.urljoin(self.url, '/'.join([f'/api/{api_version}', *args]))

    @v2endpoint
    def create_schema(self, schema):
        return self.session.post(self._build_url('stream-schemas'), json=schema, proxies=self.proxies)

    @v1endpoint
    def update_schema(self, schema):
        url_ = self._build_url('stream-schemas', 'internal', api_version='v1')
        return requests.post(
            url_, json=schema, proxies=self.proxies, params={
                'token': self.api_token,
                'id': schema["id"]
            }
        )

    @v1endpoint
    def send_watermark(self, data):
        url_ = self._build_url('metrics', 'watermark', api_version='v1')
        return requests.post(
            url_,
            json=data,
            proxies=self.proxies,
            params={
                'token': self.api_token,
                'protocol': HttpDestination.PROTOCOL_30
            }
        )

    def _delete_schema_old_api(self, schema_id):
        """
        Used for old anodot api version (for on-prem)
        :param schema_id:
        :return:
        """
        return self.session.delete(self._build_url('stream-schemas', schema_id), proxies=self.proxies)

    @v2endpoint
    def delete_schema(self, schema_id):
        try:
            res = self.session.delete(self._build_url('stream-schemas', 'schemas', schema_id), proxies=self.proxies)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return self._delete_schema_old_api(schema_id)
            raise

    @v2endpoint
    def send_topology_data(self, data_type, data):
        return self.session.post(
            self._build_url('topology', 'data'), proxies=self.proxies, data=data, params={'type': data_type}
        )

    @v2endpoint
    def send_pipeline_data_to_bc(self, pipeline_data: dict):
        return self.session.post(self._build_url('bc', 'agents'), proxies=self.proxies, json=pipeline_data)

    @v2endpoint
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

    @v2endpoint
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

    @v2endpoint
    def get_alerts(self, params: dict):
        return self.session.get(
            self._build_url('alerts', 'triggered'),
            params=params,
            proxies=self.proxies,
        )

    def get_refresh_token_url(self) -> str:
        return self._build_url('access-token')

    def get_events_url(self) -> str:
        return self._build_url('user-events')
