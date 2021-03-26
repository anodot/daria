import os
import re
import rrdtool

from datetime import datetime, timedelta
from agent.data_extractor import cacti
from agent.modules.db import Entity
from sqlalchemy import ForeignKey, Column, String, JSON, DateTime
from typing import List
from agent.pipeline import Pipeline
from agent import source
from agent.modules import logger

logger_ = logger.get_logger(__name__)


class Source:
    def __init__(self, data: dict):
        self.name = data['name']
        self.name_cache = data['name_cache']
        self.data_source_path = data['data_source_path']


class SourcesCache(Entity):
    __tablename__ = 'cacti_source_cache'

    pipeline_id = Column(String, ForeignKey('pipelines.name'), primary_key=True)
    raw_sources = Column(JSON)
    expires_at = Column(DateTime)

    def __init__(self, pipeline_id: str, raw_sources: list, expires_at):
        self.pipeline_id = pipeline_id
        self.raw_sources = raw_sources
        self.expires_at = expires_at


class SourceCacher:
    SOURCE_CACHE_TTL = 3600

    @classmethod
    def get_sources(cls, pipeline_: Pipeline) -> List[Source]:
        sources_cache = cacti.repository.get_source_cache(pipeline_)
        if sources_cache is None:
            sources_cache = cls._cache_sources(pipeline_)
        elif datetime.now() >= sources_cache.expires_at:
            cls._update_cache(sources_cache, pipeline_)
        return [Source(source_data) for source_data in sources_cache.raw_sources]

    @classmethod
    def _cache_sources(cls, pipeline_: Pipeline) -> SourcesCache:
        cache = SourcesCache(pipeline_.name, cls._fetch_raw_sources(pipeline_), cls._new_expire())
        cacti.repository.save_source_cache(cache)
        return cache

    @classmethod
    def _update_cache(cls, sources_cache: SourcesCache, pipeline_: Pipeline):
        sources_cache.raw_sources = cls._fetch_raw_sources(pipeline_)
        sources_cache.expires_at = cls._new_expire()
        cacti.repository.save_source_cache(sources_cache)

    @staticmethod
    def _fetch_raw_sources(pipeline_: Pipeline) -> list:
        res = cacti.repository.get_cacti_sources(
            pipeline_.source.config[source.CactiSource.MYSQL_CONNECTION_STRING],
            pipeline_.config.get('exclude_hosts'),
            pipeline_.config.get('exclude_datasources')
        )
        return [dict(r) for r in res]

    @classmethod
    def _new_expire(cls) -> datetime:
        return datetime.now() + timedelta(seconds=cls.SOURCE_CACHE_TTL)


def extract_metrics(pipeline_: Pipeline, start: str, end: str, step: str) -> list:
    metrics = []
    for cacti_source in SourceCacher.get_sources(pipeline_):
        base_metric = {
            'target_type': 'gauge',
            'properties': _extract_dimensions(cacti_source),
        }
        rrd_file_name = cacti_source.data_source_path
        if not rrd_file_name:
            continue

        if '<path_rra>' not in rrd_file_name:
            logger_.warning(f'Path {rrd_file_name} does not contain "<path_rra>/", skipping')
            continue

        rrd_file_path = rrd_file_name.replace('<path_rra>', pipeline_.source.config[source.CactiSource.RRD_DIR])
        if not os.path.isfile(rrd_file_path):
            logger_.warning(f'File {rrd_file_path} does not exist')
            continue
        result = rrdtool.fetch(rrd_file_path, 'AVERAGE', ['-s', start, '-e', end, '-r', step])

        # result[0][2] - is the closest available step to the step provided in the fetch command
        # if they differ - skip the source as the desired step is not available in it
        if result[0][2] != int(step):
            continue

        # contains the timestamp of the first data item
        data_start = result[0][0]
        for name_idx, measurement_name in enumerate(result[1]):
            for row_idx, data in enumerate(result[2]):
                timestamp = int(data_start) + row_idx * int(step)
                value = data[name_idx]

                # rrd might return a record for the timestamp earlier then start
                if timestamp < int(start):
                    continue
                # skip values with timestamp end in order not to duplicate them
                if timestamp >= int(end):
                    continue
                # value will be None if it's not available for the chosen consolidation function or timestamp
                if value is None:
                    continue

                metric = base_metric.copy()
                metric['properties']['what'] = measurement_name.replace(".", "_").replace(" ", "_")
                metric['value'] = value
                metric['timestamp'] = timestamp
                metrics.append(metric)
    return metrics


def _extract_dimensions(cacti_source: Source) -> dict:
    dimensions = {}
    dimension_values = _extract_dimension_values(cacti_source.name, cacti_source.name_cache)
    if not dimension_values:
        return {}
    dimension_names = _extract_dimension_names(cacti_source.name)
    if not dimension_names:
        return {}
    for i, name in enumerate(dimension_names):
        value = dimension_values[i]
        if isinstance(name, str):
            name = name.replace(".", "_").replace(" ", "_")
        if isinstance(value, str):
            value = value.replace(".", "_").replace(" ", "_")
        dimensions[name] = value
    return dimensions


def _extract_dimension_names(name: str) -> List[str]:
    # extract all values between `|`
    return re.findall('\|([^|]+)\|', name)


def _extract_dimension_values(name: str, name_cache: str) -> List[tuple]:
    regex = re.sub('(\|[^|]+\|)', '(.*)', name)
    result = re.findall(regex, name_cache)
    if not result:
        return []
    return list(result[0])
