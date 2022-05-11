import time
import base64
import json
import requests


class AnodotApiClient:
    def __init__(self, sdc_state, refresh_token_url, access_token, proxies):
        self.sdc_state = sdc_state
        self.refresh_token_url = refresh_token_url
        self.access_token = access_token
        self.proxies = proxies
        self.session = requests.Session()
        self._update_headers()

    def post(self, url, data=None, json_=None, params=None, timeout=30):
        return requests.post(
            url,
            json=json_,
            data=data,
            proxies=self.proxies,
            params=params,
            timeout=timeout,
        )

    def _get_auth_token(self):
        auth_token = self.sdc_state.get('auth_token')
        if auth_token is None or self._is_expired(auth_token):
            auth_token = self._retrieve_new_auth_token()
            self.sdc_state['auth_token'] = auth_token
            self._update_headers()
        return auth_token

    def _update_headers(self):
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self._get_auth_token()
        })

    def _retrieve_new_auth_token(self):
        response = requests.post(
            self.refresh_token_url,
            json={'refreshToken': self.access_token},
            proxies=self.proxies
        )
        response.raise_for_status()
        return response.text.replace('"', '')

    @staticmethod
    def _is_expired(auth_token):
        res = auth_token.split('.')[1]
        res = base64.b64decode(res)
        expiration_timestamp = json.loads(res)['exp']
        # refresh token in advance just in case
        return expiration_timestamp < time.time() - 300
