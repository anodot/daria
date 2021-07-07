import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from agent.modules import constants


class Adapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=constants.TLS_VERSION,
            **pool_kwargs
        )


class Session(requests.Session):
    def __init__(self):
        super(Session, self).__init__()
        self.mount('https://', Adapter())
