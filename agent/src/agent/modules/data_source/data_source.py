from abc import ABC, abstractmethod
from agent.modules import data_source

FILE_SOURCE = 'file'
API_SOURCE = 'API'

SOURCE_TYPES = [FILE_SOURCE, API_SOURCE]


class DataSource(ABC):
    @abstractmethod
    def get_data(self) -> list[dict]:
        pass


def build(source_config: dict) -> DataSource:
    type_ = source_config['type']
    if type_ == FILE_SOURCE:
        return data_source.File(source_config['path'], source_config['format'])
    elif type_ == API_SOURCE:
        return data_source.API(source_config['url'], source_config['authentication'])
    else:
        raise Exception(
            (f'Invalid entity source type provided: `{type_}`\n'
             f'Available types are: {",".join(SOURCE_TYPES)}')
        )
