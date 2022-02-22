import csv
import json

from abc import ABC, abstractmethod
from agent.modules.data_source.data_source import DataSource

CSV = 'CSV'
JSON = 'JSON'


class File(DataSource):
    def __init__(self, path: str, format_: str):
        self.path: str = path
        self.format: str = format_

    def get_data(self) -> list[dict]:
        return _get_file_loader(self.format).load(self.path)


class FileLoader(ABC):
    @staticmethod
    @abstractmethod
    def load(path: str) -> list[dict]:
        pass


class CSVLoader(FileLoader):
    @staticmethod
    def load(path: str) -> list[dict]:
        if '/usr/src/app/' in path:
            path = path.replace('/usr/src/app/', '/Users/antonzelenin/Workspace/daria/agent/')
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


def _get_file_loader(format_: str) -> FileLoader:
    if format_ == CSV:
        return CSVLoader()
    elif format_ == JSON:
        return JSONLoader()
    else:
        raise Exception(f'Invalid file format provided - `{format_}`')
