from datetime import datetime, timedelta
from sqlalchemy import Column, String, ForeignKey, JSON, DateTime
from agent import source
from agent.data_extractor import cacti
from agent.modules.db import Entity
from agent.pipeline import Pipeline, List


class SourcesCache(Entity):
    __tablename__ = 'cacti_source_cache'

    pipeline_id = Column(String, ForeignKey('pipelines.name'), primary_key=True)
    raw_sources = Column(JSON)
    expires_at = Column(DateTime)

    def __init__(self, pipeline_id: str, raw_sources: list, expires_at):
        self.pipeline_id = pipeline_id
        self.raw_sources = raw_sources
        self.expires_at = expires_at


def get_sources(pipeline_: Pipeline) -> List[cacti.Source]:
    sources_cache = cacti.repository.get_source_cache(pipeline_)
    if sources_cache is None:
        sources_cache = _cache_sources(pipeline_)
    elif datetime.now() >= sources_cache.expires_at:
        _update_cache(sources_cache, pipeline_)
    return [cacti.Source(source_data) for source_data in sources_cache.raw_sources]


def _cache_sources(pipeline_: Pipeline) -> SourcesCache:
    cache = SourcesCache(
        pipeline_.name,
        _fetch_raw_sources(pipeline_),
        _new_expire(int(pipeline_.config['source_cache_ttl']))
    )
    cacti.repository.save_source_cache(cache)
    return cache


def _update_cache(sources_cache: SourcesCache, pipeline_: Pipeline):
    sources_cache.raw_sources = _fetch_raw_sources(pipeline_)
    sources_cache.expires_at = _new_expire(int(pipeline_.config['source_cache_ttl']))
    cacti.repository.save_source_cache(sources_cache)


def _fetch_raw_sources(pipeline_: Pipeline) -> list:
    res = cacti.repository.get_cacti_sources(
        pipeline_.source.config[source.CactiSource.MYSQL_CONNECTION_STRING],
        pipeline_.config.get('exclude_hosts'),
        pipeline_.config.get('exclude_datasources')
    )
    return [dict(r) for r in res]


def _new_expire(ttl_seconds: int) -> datetime:
    return datetime.now() + timedelta(seconds=ttl_seconds)
