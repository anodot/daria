import time
import base64
import json
import requests


class AnodotUrlBuilder:
    def __init__(self, base_url):
        self.base_url = base_url
        self.base_url = self.base_url.rstrip('/')

    def build(self, *args):
        paths = ['/api/v2']
        paths.extend(args)
        return self.base_url + '/'.join(paths)


class AnodotApiClient:
    def __init__(self, sdc_state, anodot_url, access_token, proxies):
        self.url_builder = AnodotUrlBuilder(anodot_url)
        self.sdc_state = sdc_state
        self.access_token = access_token
        self.proxies = proxies
        self.session = requests.Session()
        self._update_headers()

    def start_topology_data_load(self):
        return self._post(self.url_builder.build('topology', 'map', 'load', 'start'))

    def end_topology_data_load(self, rollup_id):
        # rollup end might take several minutes so make sure we wait enough
        return self._post(self.url_builder.build('topology', 'map', 'load', rollup_id, 'end'), timeout=300)

    def send_topology_data(self, data, rollup_id):
        return self._put(self.url_builder.build('topology', 'map', 'load', rollup_id), json_=data)

    def send_events(self, events):
        return self._post(self.url_builder.build('user-events'), json_=events)

    def _post(self, url, data=None, json_=None, params=None, timeout=30):
        return self.session.post(
            url,
            json=json_,
            data=data,
            proxies=self.proxies,
            params=params,
            timeout=timeout,
        )

    def _put(self, url, data=None, json_=None, params=None, timeout=30):
        return self.session.put(
            url,
            json=json_,
            data=data,
            proxies=self.proxies,
            params=params,
            timeout=timeout,
        )

    # todo this shit regularly returns 401 and it can't re-authorize
    def _get_auth_token(self):
        auth_token = self.sdc_state.get('auth_token')
        if auth_token is None or self._is_expired(auth_token):
            auth_token = self._retrieve_new_auth_token()
            self.sdc_state['auth_token'] = auth_token
        return auth_token

    def _update_headers(self):
        self.session.headers.update({
            'Content-Type': 'application/json',
            # it must be explicitly converted to string
            # because streamsets will make it a unicode string and authorization will not work
            'Authorization': str('Bearer ' + self._get_auth_token()),
        })

    def _retrieve_new_auth_token(self):
        response = requests.post(
            self._get_refresh_token_url(), json={'refreshToken': self.access_token}, proxies=self.proxies
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

    def _get_refresh_token_url(self):
        return self.url_builder.build('access-token')
