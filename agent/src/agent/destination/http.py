import json
import os
import urllib.parse

from agent.constants import ANODOT_API_URL, DATA_DIR


class HttpDestination:
    FILE = os.path.join(DATA_DIR, 'destination.json')
    TYPE = 'http'

    def __init__(self):
        self.config = self.load() if self.exists() else {'config': {}, 'type': self.TYPE}

    @classmethod
    def exists(cls):
        return os.path.isfile(cls.FILE)

    @classmethod
    def load(cls):
        if not cls.exists():
            raise DestinationException('Destination wasn\'t configured')

        with open(cls.FILE, 'r') as f:
            return json.load(f)

    @staticmethod
    def get_url(token):
        return urllib.parse.urljoin(ANODOT_API_URL, f'api/v1/metrics?token={token}&protocol=anodot20')

    def save(self):
        with open(self.FILE, 'w') as f:
            json.dump(self.config, f)


class DestinationException(Exception):
    pass
