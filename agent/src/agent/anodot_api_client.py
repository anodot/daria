import requests
import urllib.parse
import click

from .logger import get_logger

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

    def __init__(self, api_key, proxies, base_url='https://app.anodot.com'):
        """

        :param api_key: api_key
        :param base_url: string
        """
        self.api_key = api_key
        self.base_url = base_url
        self.proxies = proxies
        self.session = requests.Session()
        self.get_auth_token()

    def get_auth_token(self):
        auth_token = self.session.post(self.build_url('access-token'),
                                       json={'refreshToken': self.api_key},
                                       proxies=self.proxies)
        auth_token.raise_for_status()
        self.session.headers.update({'Authorization': 'Bearer ' + auth_token.text.replace('"', '')})

    def build_url(self, *args):
        """
        Build url for endpoints
        :param args:
        :return: string
        """
        return urllib.parse.urljoin(self.base_url, '/'.join(['/api/v2', *args]))

    @endpoint
    def create_schema(self, schema):
        return self.session.post(self.build_url('stream-schemas'), json=schema, proxies=self.proxies)

    @endpoint
    def delete_schema(self, schema_id):
        return self.session.delete(self.build_url('stream-schemas', schema_id), params={'deleteOrigin': 'false'},
                                   proxies=self.proxies)
