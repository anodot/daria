from datetime import datetime, timedelta
from sqlalchemy import Column, String, ForeignKey, JSON, DateTime
from agent import pipeline, source
from agent.data_extractor import cacti
from agent.modules.db import Entity


class CactiCache(Entity):
    GRAPHS = 'graphs'
    HOSTS = 'hosts'

    __tablename__ = 'cacti_cache'

    pipeline_id = Column(String, ForeignKey('pipelines.name'), primary_key=True)
    data = Column(JSON)
    expires_at = Column(DateTime)

    def __init__(self, pipeline_id: str, data: dict, expires_at):
        self.pipeline_id = pipeline_id
        self.data = data
        self.expires_at = expires_at

    def _get(self, key: str):
        return self.data[key]

    @property
    def graphs(self) -> dict:
        return self._get(self.GRAPHS)

    @property
    def hosts(self) -> dict:
        return self._get(self.HOSTS)

    def is_expired(self) -> bool:
        return self.expires_at >= datetime.now()


def cache_data():
    for pipeline_ in pipeline.repository.get_by_type(source.TYPE_CACTI):
        cache = cacti.repository.get_cache(pipeline_)
        if cache is None or cache.is_expired():
            data = cacti.repository.CactiCacher(pipeline_.source.config[source.CactiSource.MYSQL_CONNECTION_STRING]).get_data()
            if cache is None:
                cache = cacti.cacher.CactiCache(
                    pipeline_.name,
                    data,
                    _new_expire(pipeline_.source.config.get('cache_ttl', 3600))
                )
            else:
                cache.data = data
            cacti.repository.save_cacti_cache(cache)


def _new_expire(ttl_seconds: int) -> datetime:
    return datetime.now() + timedelta(seconds=ttl_seconds)
