import sdc_client

from typing import Optional, List
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from agent.modules import tools, field
from agent.modules.constants import HOSTNAME
from agent.modules.db import Entity
from agent.destination import HttpDestination, DummyHttpDestination
from enum import Enum
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, func, Float, Boolean
from copy import deepcopy
from agent import source, pipeline
from agent.modules.time import Interval
from agent.source import Source
from agent.streamsets import StreamSets

TYPE = 'pipeline_type'

REGULAR_PIPELINE = 'regular_pipeline'
RAW_PIPELINE = 'raw_pipeline'
EVENTS_PIPELINE = 'events_pipeline'
TOPOLOGY_PIPELINE = 'topology_pipeline'

PIPELINE_TYPES = [REGULAR_PIPELINE, RAW_PIPELINE, EVENTS_PIPELINE, TOPOLOGY_PIPELINE]


class PipelineException(Exception):
    pass


class TimestampType(Enum):
    STRING = 'string'
    UTC_STRING = 'utc_string'
    DATETIME = 'datetime'
    UNIX = 'unix'
    UNIX_MS = 'unix_ms'


class FlushBucketSize(Interval):
    pass


class Pipeline(Entity, sdc_client.IPipeline):
    __tablename__ = 'pipelines'

    STATUS_RUNNING = 'RUNNING'
    STATUS_STOPPED = 'STOPPED'
    STATUS_EDITED = 'EDITED'
    STATUS_RETRY = 'RETRY'
    STATUS_STOPPING = 'STOPPING'
    STATUS_STARTING = 'STARTING'
    STATUS_RUN_ERROR = 'RUN_ERROR'
    STATUS_START_ERROR = 'START_ERROR'
    STATUS_STOP_ERROR = 'STOP_ERROR'
    STATUS_RUNNING_ERROR = 'RUNNING_ERROR'
    OVERRIDE_SOURCE = 'override_source'
    FLUSH_BUCKET_SIZE = 'flush_bucket_size'

    COUNTER = 'counter'
    GAUGE = 'gauge'
    RUNNING_COUNTER = 'running_counter'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    source_id = Column(Integer, ForeignKey('sources.id'))
    destination_id = Column(Integer, ForeignKey('destinations.id'), nullable=True)
    config = Column(JSON)
    schema = Column(JSON)
    override_source = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    last_edited = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now())
    status = Column(String, default=STATUS_EDITED)
    streamsets_id = Column(Integer, ForeignKey('streamsets.id'))

    offset = relationship("PipelineOffset", cascade="delete", uselist=False)
    watermark = relationship("PipelineWatermark", cascade="delete", uselist=False)
    source_ = relationship('Source', back_populates='pipelines')
    destination = relationship('HttpDestination', cascade="merge")
    streamsets = relationship('StreamSets')
    retries = relationship('PipelineRetries', cascade="delete", uselist=False)

    def __init__(self, pipeline_id: str, source_: Source, destination: HttpDestination):
        self.name = pipeline_id
        self._previous_config = {}
        self._previous_override_source = {}
        self.config = {}
        self.source_ = source_
        self.source_id = source_.id
        self.destination = destination
        self.destination_id = destination.id
        self.override_source = {}
        self.streamsets_id = None
        self.streamsets = None
        self.type = REGULAR_PIPELINE

    def config_changed(self) -> bool:
        if not hasattr(self, '_previous_config'):
            return False
        return self.config != self._previous_config or self.override_source != self._previous_override_source

    def set_config(self, config: dict):
        self._previous_config = deepcopy(self.config)
        self._previous_override_source = deepcopy(self.override_source)
        self.override_source = config.pop(self.OVERRIDE_SOURCE, {})
        self.config = deepcopy(config)

    @property
    def source(self) -> Source:
        return self.source_

    def has_periodic_watermark_config(self) -> bool:
        return bool(self.config.get('periodic_watermark'))

    def has_offset(self) -> bool:
        return bool(self.offset)

    def has_watermark(self) -> bool:
        return bool(self.watermark)

    @property
    def periodic_watermark_config(self) -> dict:
        return self.config.get('periodic_watermark', {})

    @property
    def watermark_delay(self) -> int:
        return self.config.get('periodic_watermark', {}).get('delay', 0)

    @property
    def flush_bucket_size(self) -> FlushBucketSize:
        return FlushBucketSize(self.config.get(self.FLUSH_BUCKET_SIZE, '1d'))

    @flush_bucket_size.setter
    def flush_bucket_size(self, value: str):
        self.config[self.FLUSH_BUCKET_SIZE] = FlushBucketSize(value).value

    @property
    def static_dimensions(self) -> dict:
        return self.config.get('properties', {})

    @property
    def static_dimension_names(self) -> list:
        return [tools.replace_illegal_chars(s_dim) for s_dim in self.static_dimensions.keys()]

    @property
    def dimensions(self) -> list | dict:
        return self.config.get('dimensions', [])

    @property
    def dimension_paths(self) -> list:
        return [self._get_property_path(value) for value in self.all_dimensions]

    @property
    def required_dimensions(self) -> list:
        if type(self.dimensions) is list:
            return []
        return self.dimensions.get('required', [])

    @property
    def required_dimension_paths(self) -> list:
        return [self._get_property_path(value) for value in self.required_dimensions]

    @property
    def optional_dimensions(self) -> list:
        if type(self.dimensions) is list:
            return []
        return self.dimensions.get('optional', [])

    @property
    def all_dimensions(self) -> list:
        if not self.dimensions or type(self.dimensions) is list:
            return self.dimensions + self.static_dimension_names
        return self.required_dimensions + self.optional_dimensions + self.static_dimension_names

    @property
    def dimension_names(self) -> list:
        return [tools.replace_illegal_chars(d.replace('/', '_')) for d in self.all_dimensions]

    @property
    def dimension_paths_with_names(self) -> dict:
        return dict(zip(self.dimension_paths, self.dimension_names))

    @property
    def dimension_configurations(self) -> Optional[dict]:
        if not isinstance(self.dimensions, list):
            raise PipelineException((
                'Pipeline dimensions should be a list in order to build dimension_configurations, '
                f'but {type(self.dimensions).__name__} provided'
            ))
        return _build_transformation_configurations(self.dimensions, self.config.get('dimension_configurations'))

    @property
    def measurement_configurations(self) -> Optional[dict]:
        return _build_transformation_configurations(
            list(self.values),
            self.config.get('measurement_configurations', {}),
        )

    @property
    def tag_configurations(self) -> Optional[dict]:
        return self.config.get('tag_configurations', {})

    @property
    def timestamp_path(self) -> str:
        return self._get_property_path(self.config['timestamp']['name'])

    @property
    def timezone(self) -> str:
        return self.config.get('timezone', 'UTC')

    @property
    def timestamp_type(self) -> TimestampType:
        return TimestampType(self.config['timestamp']['type'])

    @property
    def timestamp_name(self) -> Optional[str]:
        return self.config.get('timestamp', {}).get('name')

    @property
    def timestamp_format(self) -> str:
        return self.config['timestamp'].get('format')

    @property
    def values(self) -> dict:
        return self.config.get('values', {})

    @property
    def value_paths(self) -> list:
        return [self._get_property_path(value) for value in self.values.keys()]

    @property
    def target_types(self) -> list:
        if self.source.type == source.TYPE_INFLUX:
            return [self.config.get('target_type', 'gauge')] * len(self.value_paths)
        return list(self.values.values())

    @property
    def measurement_paths_with_names(self) -> dict:
        return dict(zip(self.config.get('measurement_names', {}).keys(), self.measurement_names))

    @property
    def measurement_names(self) -> list:
        return [
            tools.replace_illegal_chars(self.config.get('measurement_names', {}).get(key, key))
            for key in self.values.keys()
        ]

    @property
    def measurement_names_with_target_types(self) -> dict:
        result = {}
        measurement_names = self.config.get('measurement_names', {})
        for measurement, target_type in self.values.items():
            measurement_name = measurement_names.get(measurement, measurement)
            measurement_name = tools.replace_illegal_chars(measurement_name)
            result[measurement_name] = target_type
        return result

    @property
    def measurement_names_paths(self):
        return [self._get_property_path(value) for value in self.measurement_names]

    @property
    def value_paths_with_names(self) -> dict:
        # value_paths should work the same as value_names that were here
        # value_paths are needed for directory and kafka and mb something else
        return dict(zip(self.value_paths, self.measurement_names))

    @property
    def target_types_paths(self):
        return [self._get_property_path(t_type) for t_type in self.target_types]

    @property
    def count_records(self) -> bool:
        return self.config.get('count_records', False)

    @property
    def count_records_measurement_name(self) -> str:
        return tools.replace_illegal_chars(self.config.get('count_records_measurement_name', 'count'))

    @property
    def static_what(self) -> bool:
        return self.config.get('static_what', True)

    @property
    def transformations_config(self) -> str:
        return self.config.get('transform', {}).get('config')

    @property
    def filter_condition(self) -> str:
        return self.config.get('filter', {}).get('condition')

    @property
    def tags(self) -> dict:
        return self.config.get('tags', {})

    @property
    def values_array_path(self) -> str:
        return self.config.get('values_array_path', '')

    @property
    def values_array_filter_metrics(self) -> list:
        return self.config.get('values_array_filter_metrics', [])

    @property
    def query_file(self) -> Optional[str]:
        return self.config.get('query_file')

    @property
    def query(self) -> Optional[str]:
        return self.config.get('query')

    @query.setter
    def query(self, query: str):
        self.config['query'] = query

    @property
    def interval(self) -> Optional[int]:
        # returns interval in seconds
        interval = self.config.get('interval')
        if interval in Interval.VALUES:
            return Interval(interval).total_seconds()
        return int(interval) if interval is not None else None

    @property
    def days_to_backfill(self) -> str:
        return str(self.config.get('days_to_backfill', '0'))

    @property
    def delay(self) -> str:
        return self.config.get('delay', '0')

    @property
    def watermark_in_local_timezone(self) -> str:
        return self.config.get('watermark_in_local_timezone', False)

    @property
    def batch_size(self) -> str:
        return self.config.get('batch_size', '1000')

    def uses_schema(self) -> bool:
        return bool(self.config.get('uses_schema'))

    @property
    def histories_batch_size(self) -> str:
        return self.config.get('histories_batch_size', '100')

    @property
    def header_attributes(self) -> list:
        return self.config.get('header_attributes', [])

    @property
    def log_everything(self) -> bool:
        return bool(self.config.get('log_everything'))

    @property
    def transform_script_config(self) -> str:
        return self.config.get('transform_script', {}).get('config', '')

    @property
    def watermark_sleep_time(self) -> int:
        return self.config.get('watermark_sleep_time', 10)

    @property
    def lookups(self) -> dict:
        return self.config.get('lookups', {})

    @property
    def is_strict(self) -> bool:
        return bool(self.config.get('strict', True))

    @property
    def dvp_config(self) -> dict:
        return self.config.get('dvpConfig', {})

    @property
    def dynamic_step(self) -> bool:
        return bool(self.config.get('dynamic_step', False))

    def get_streamsets_config(self) -> dict:
        return pipeline.manager.create_streamsets_pipeline_config(self)

    def get_id(self) -> str:
        return self.name

    def get_offset(self) -> Optional[str]:
        return self.offset.offset if self.offset else None

    def get_streamsets(self) -> Optional[sdc_client.IStreamSets]:
        return self.streamsets

    def set_streamsets(self, streamsets_: StreamSets):
        self.streamsets_id = streamsets_.id
        self.streamsets = streamsets_

    def delete_streamsets(self):
        self.streamsets_id = None
        self.streamsets = None

    def get_schema(self) -> dict:
        return self.schema or {}

    def has_schema(self) -> bool:
        return bool(self.schema)

    def get_schema_id(self) -> Optional[str]:
        return self.get_schema().get('id')

    def export(self) -> dict:
        return {
            **self.config,
            self.OVERRIDE_SOURCE: self.override_source,
            'pipeline_id': self.name,
            'source': self.source.name,
        }

    def to_dict(self) -> dict:
        return {
            'id': self.name,
            'config': self.config,
            'schema': self.get_schema(),
            'override_source': self.override_source,
            'source': self.source.config,
            'destination': self.destination.config,
        }

    def _get_property_path(self, property_value: str) -> str:
        for idx, item in self.source.config.get('csv_mapping', {}).items():
            if item == property_value:
                return str(idx)
        if property_value in self.config.get('dimension_value_paths', {}):
            return str(self.config.get('dimension_value_paths', {})[property_value])
        return property_value

    def meta_tags(self) -> dict:
        return {
            'source': ['anodot-agent'],
            'source_host_id': [self.destination.host_id],
            'source_host_name': [tools.replace_illegal_chars(HOSTNAME)],
            'pipeline_id': [self.name],
            'pipeline_type': [self.source.type]
        }

    def get_tags(self) -> dict:
        return {**self.meta_tags(), **self.tags}

    def error_notification_enabled(self) -> bool:
        return not self.config.get('disable_error_notifications', False)


class RawPipeline(Pipeline):
    def __init__(self, pipeline_id: str, source_: Source):
        super(RawPipeline, self).__init__(pipeline_id, source_, DummyHttpDestination())
        self.type = RAW_PIPELINE


class TopologyPipeline(Pipeline):
    def __init__(self, pipeline_id: str, source_: Source, destination_: HttpDestination):
        super(TopologyPipeline, self).__init__(pipeline_id, source_, destination_)
        self.type = TOPOLOGY_PIPELINE


class EventsPipeline(Pipeline):
    def __init__(self, pipeline_id: str, source_: Source, destination_: HttpDestination):
        super(EventsPipeline, self).__init__(pipeline_id, source_, destination_)
        self.type = EVENTS_PIPELINE


class TestPipeline(Pipeline):
    def __init__(self, pipeline_id: str, source_):
        super().__init__(pipeline_id, source_, DummyHttpDestination())

    def get_schema_id(self) -> str:
        return 'dummy_schema_id'


class PipelineOffset(Entity):
    __tablename__ = 'pipeline_offsets'

    id = Column(Integer, primary_key=True)
    pipeline_id = Column(Integer, ForeignKey('pipelines.id'))
    offset = Column(String)
    timestamp = Column(Float)

    def __init__(self, pipeline_id: int, offset: str, timestamp: float):
        self.pipeline_id = pipeline_id
        self.offset = offset
        self.timestamp = timestamp


class PipelineWatermark(Entity):
    __tablename__ = 'pipeline_watermarks'

    pipeline_id = Column(Integer, ForeignKey('pipelines.name'), primary_key=True)
    timestamp = Column(Float)

    def __init__(self, pipeline_id: str, timestamp: float):
        self.pipeline_id = pipeline_id
        self.timestamp = timestamp


class Provider(sdc_client.IPipelineProvider):
    def get_all(self) -> List[Pipeline]:
        return pipeline.repository.get_all()

    def save(self, pipeline_: Pipeline):
        pipeline.repository.save(pipeline_)


class PipelineRetries(Entity):
    __tablename__ = 'pipeline_retries'

    pipeline_id = Column(String, ForeignKey('pipelines.name'), primary_key=True)
    number_of_error_statuses = Column(Integer)
    notification_sent = Column(Boolean, default=False)
    last_updated = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now())

    def __init__(self, pipeline_: Pipeline):
        self.pipeline_id = pipeline_.name
        self.number_of_error_statuses = 0
        self.notification_sent = False


class PipelineMetric:
    REQUIRED_KEYS = ['counters']

    def __init__(self, metrics_: dict):
        for key in self.REQUIRED_KEYS:
            if key not in metrics_:
                raise KeyError(f'The key `{key}` not in input dict')

        self.stat_in = metrics_['counters']['pipeline.batchInputRecords.counter']['count']
        self.stat_out = metrics_['counters']['pipeline.batchOutputRecords.counter']['count']
        self.errors = metrics_['counters']['pipeline.batchErrorRecords.counter']['count']
        self.errors_perc = self.errors * 100 / self.stat_in if self.stat_in != 0 else 0

    def __str__(self):
        return f'In: {self.stat_in} - Out: {self.stat_out} - Errors {self.errors} ({self.errors_perc:.1f}%)'

    def has_error(self):
        return self.errors > 0

    def has_undelivered(self):
        return self.stat_out == 0


def _build_transformation_configurations(values: list, configurations: dict) -> dict:
    """
    Configurations could be either dimensions_configurations or measurement_configurations.
    Dimension or measurement configurations are optional for a pipeline, this function adds dimensions or
    measurements that are not in the dimension_configurations or measurement_configurations respectively and
    sets their value path to be the same as the dimension or measurement itself.
    Doing so allows working with only one config dimension_configurations instead of using two
    """
    for item in values:
        if item not in configurations:
            configurations[item] = {field.Variable.VALUE_PATH: item}
    return configurations
