import requests
import requests.packages.urllib3
import urllib.parse

from typing import Optional
from agent.destination import HttpDestination, AuthenticationToken
from agent.modules import proxy
from agent.modules.logger import get_logger
from agent import destination

from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

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


class AnodotUrlBuilder:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def build(self, *args, api_version='v2') -> str:
        return urllib.parse.urljoin(self.base_url, '/'.join([f'/api/{api_version}', *args]))


class MonitoringApiClient:
    def __init__(self, destination_url: str, access_token: str, proxy_: destination.Proxy, verify_ssl=True):
        self.access_token = access_token
        self.proxies = proxy.get_config(proxy_)
        self.url_builder = AnodotUrlBuilder(destination_url)
        self.params = {'token': access_token, 'protocol': destination.HttpDestination.PROTOCOL_20}
        self.verify_ssl = verify_ssl

    @v2endpoint
    def send_to_client(self, data: list[dict]):
        return requests.post(
            self.url_builder.build('metrics/', api_version='v1'),
            json=data,
            params=self.params,
            proxies=self.proxies,
            verify=self.verify_ssl
        )

    @v1endpoint
    def send_to_anodot(self, data: list[dict]):
        return requests.post(
            self.url_builder.build('agents', api_version='v1'),
            json=data,
            params=self.params,
            proxies=self.proxies,
            verify=self.verify_ssl
        )


class AnodotApiClient:
    def __init__(self, destination_: HttpDestination):
        self.url = destination_.url
        self.access_key = destination_.access_key
        self.api_token = destination_.token
        self.proxies = proxy.get_config(destination_.proxy)
        self.url_builder = AnodotUrlBuilder(destination_.url)
        self.verify_ssl = not destination_.use_jks_truststore
        self.session = requests.Session()
        self.session.verify = self.verify_ssl
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
            self.get_refresh_token_url(),
            json={'refreshToken': self.access_key},
            proxies=self.proxies,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.text.replace('"', '')

    @v2endpoint
    def create_schema(self, schema):
        return self.session.post(self.url_builder.build('stream-schemas'), json=schema, proxies=self.proxies)

    @v1endpoint
    def update_schema(self, schema):
        return requests.post(
            self.url_builder.build('stream-schemas', 'internal', api_version='v1'),
            json=schema,
            proxies=self.proxies,
            verify=self.verify_ssl,
            params={
                'token': self.api_token,
                'id': schema["id"]
            }
        )

    @v1endpoint
    def send_watermark(self, data):
        return requests.post(
            self.url_builder.build('metrics', 'watermark', api_version='v1'),
            verify=self.verify_ssl,
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
        return self.session.delete(self.url_builder.build('stream-schemas', schema_id), proxies=self.proxies)

    @v2endpoint
    def delete_schema(self, schema_id):
        try:
            res = self.session.delete(
                self.url_builder.build('stream-schemas', 'schemas', schema_id), proxies=self.proxies
            )
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return self._delete_schema_old_api(schema_id)
            raise

    @v1endpoint
    def delete_metrics(self, pipeline_id):
        data = {
            'expression': [
                {
                    'type': 'property',
                    'key': '#pipeline_id',
                    'value': f'{pipeline_id}',
                    'isExact': 'true'
                }
            ]
        }
        return self.session.delete(
            self.url_builder.build('metrics', api_version='v1'),
            proxies=self.proxies,
            json=data,
            params={
                'token': self.api_token,
                'protocol': HttpDestination.PROTOCOL_20
            }
        )

    @v2endpoint
    def send_topology_data(self, data_type, data):
        return self.session.post(
            self.url_builder.build('topology', 'data'), proxies=self.proxies, data=data, params={'type': data_type}
        )

    @v2endpoint
    def send_pipeline_data_to_bc(self, pipeline_data: dict):
        return self.session.post(self.url_builder.build('bc', 'agents'), proxies=self.proxies, json=pipeline_data)

    @v2endpoint
    def delete_pipeline_from_bc(self, pipeline_id: str):
        return self.session.delete(
            self.url_builder.build('bc', 'agents'),
            proxies=self.proxies,
            params={'pipelineId': pipeline_id},
        )

    def _get_schemas_old_api(self):
        """
        Used for old anodot api version (for on-prem)
        :return:
        """
        return self.session.get(
            self.url_builder.build('stream-schemas'), params={'excludeCubes': True}, proxies=self.proxies
        )

    @v2endpoint
    def get_schemas(self):
        try:
            res = self.session.get(
                self.url_builder.build('stream-schemas', 'schemas'),
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
            self.url_builder.build('alerts', 'triggered'),
            params=params,
            proxies=self.proxies,
        )

    def get_refresh_token_url(self) -> str:
        return self.url_builder.build('access-token')
