import json
import requests
import csv

from abc import ABC, abstractmethod
from requests.auth import HTTPBasicAuth

# todo this module should be more generic, not only for entity, it's a general data source

# todo this is source type
FILE_SOURCE_TYPE = 'file'
API_SOURCE_TYPE = 'API'

# todo this is source file type
CSV = 'CSV'
JSON = 'JSON'


class FileLoader(ABC):
    @staticmethod
    @abstractmethod
    def load(path: str) -> list[dict]:
        pass


class CSVLoader(FileLoader):
    @staticmethod
    def load(path: str) -> list[dict]:
        with open(path) as f:
            reader = csv.reader(f)
            rows = list(reader)
            header = rows.pop(0)
            return [{header[i]: val for i, val in enumerate(row)} for row in rows]


class JSONLoader(FileLoader):
    @staticmethod
    def load(path: str) -> list[dict]:
        with open(path) as f:
            return json.load(f)


# todo it can be generic, not only for entity source
def _get_file_loader(format_: str) -> FileLoader:
    if format_ == CSV:
        return CSVLoader()
    elif format_ == JSON:
        return JSONLoader()
    else:
        raise Exception(f'Invalid file format provided - `{format_}`')


class Source(ABC):
    @abstractmethod
    def get_data(self) -> list[dict]:
        pass


class File(Source):
    def __init__(self, path: str, format_: str):
        self.path: str = path
        self.format: str = format_

    def get_data(self) -> list[dict]:
        return _get_file_loader(self.format).load(self.path)


class API(Source):
    def __init__(self, url: str, authentication):
        self.url: str = url
        self.authentication = authentication

    def get_data(self) -> list[dict]:
        # todo
        # self.url = 'http://127.0.0.1:8080/api/v1/site'
        res = requests.get(self.url, auth=self.authentication)
        res.raise_for_status()
        return res.json()


# todo this is authentication type
BASIC = 'basic'


def _get_authentication(config: dict):
    type_ = config['type']
    if type_ == BASIC:
        return HTTPBasicAuth(config['username'], config['password'])
    else:
        raise Exception(f'Invalid authentication type provided: `{type_}`')


def build(source_config: dict) -> Source:
    type_ = source_config['type']
    if type_ == FILE_SOURCE_TYPE:
        # todo default value csv is not obvious
        return File(source_config['path'], source_config.get('format', CSV))
    elif type_ == API_SOURCE_TYPE:
        return API(source_config['url'], _get_authentication(source_config['authentication']))
    else:
        raise Exception(f'Invalid entity source type provided: `{type_}`')
