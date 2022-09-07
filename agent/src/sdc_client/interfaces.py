from abc import ABC, abstractmethod
from typing import Optional, List


class IStreamSets(ABC):
    @abstractmethod
    def get_id(self) -> int:
        pass

    @abstractmethod
    def get_url(self) -> str:
        pass

    @abstractmethod
    def get_username(self) -> str:
        pass

    @abstractmethod
    def get_password(self) -> str:
        pass


class IPipeline(ABC):
    STATUS_RUNNING = 'RUNNING'
    STATUS_STOPPED = 'STOPPED'
    STATUS_RETRY = 'RETRY'
    STATUS_STOPPING = 'STOPPING'
    STATUS_STARTING = 'STARTING'

    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def get_streamsets_config(self) -> dict:
        pass

    @abstractmethod
    def get_offset(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_streamsets(self) -> Optional[IStreamSets]:
        pass

    @abstractmethod
    def set_streamsets(self, streamsets_: IStreamSets):
        pass

    @abstractmethod
    def delete_streamsets(self):
        pass


class IStreamSetsProvider(ABC):
    @abstractmethod
    def get(self, id_: int) -> IStreamSets:
        pass

    @abstractmethod
    def get_all(self) -> List[IStreamSets]:
        pass


class IPipelineProvider(ABC):
    @abstractmethod
    def get_all(self) -> List[IPipeline]:
        pass

    @abstractmethod
    def save(self, pipeline: IPipeline):
        pass


class ILogger(ABC):
    @abstractmethod
    def info(self, message: str):
        pass

    @abstractmethod
    def error(self, message: str):
        pass

    @abstractmethod
    def warning(self, message: str):
        pass
