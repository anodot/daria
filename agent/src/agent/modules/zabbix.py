import requests


class Client:
    def __init__(self, url: str, user: str, password: str, verify_ssl=True):
        self.url = url + '/api_jsonrpc.php'
        self.auth_token = None
        self.verify_ssl = verify_ssl
        self._authenticate(user, password)

    def post(self, method: str, params: dict) -> list:
        res = requests.post(
            self.url,
            json={
                'jsonrpc': '2.0',
                'method': method,
                'params': params,
                'id': 1,
                'auth': self.auth_token,
            },
            verify=self.verify_ssl
        )
        res.raise_for_status()
        result = res.json()
        if 'error' in result:
            raise ZabbixClientException(str(result))
        return result['result']

    def _authenticate(self, user: str, password: str):
        self.auth_token = self.post('user.login', {'user': user, 'password': password})


class ZabbixClientException(Exception):
    pass
