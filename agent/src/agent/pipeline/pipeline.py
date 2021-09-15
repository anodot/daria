import sdc_client

from typing import Optional, List
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from agent.modules import tools
from agent.modules.constants import HOSTNAME
from agent.modules.db import Entity
from agent.destination import HttpDestination
from enum import Enum
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, func
from copy import deepcopy
from agent import source, pipeline
from agent.modules.time import Interval
from agent.source import Source
from agent.streamsets import StreamSets


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

    error_statuses = [STATUS_RUN_ERROR, STATUS_START_ERROR, STATUS_STOP_ERROR, STATUS_RUNNING_ERROR]
    # TODO make it enum
    statuses = [STATUS_EDITED, STATUS_STARTING, STATUS_RUNNING, STATUS_STOPPING, STATUS_STOPPED, STATUS_RETRY,
                STATUS_RUN_ERROR, STATUS_START_ERROR, STATUS_STOP_ERROR, STATUS_RUNNING_ERROR]

    TARGET_TYPES = [COUNTER, GAUGE, RUNNING_COUNTER]

    id = Column(Integer, primary_key=True)
    name = Column(String)
    source_id = Column(Integer, ForeignKey('sources.id'))
    destination_id = Column(Integer, ForeignKey('destinations.id'))
    config = Column(JSON)
    schema = Column(JSON)
    override_source = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    last_edited = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now())
    status = Column(String, default=STATUS_EDITED)
    streamsets_id = Column(Integer, ForeignKey('streamsets.id'))

    offset = relationship("PipelineOffset", cascade="delete", uselist=False)
    source_ = relationship('Source', back_populates='pipelines')
    destination = relationship('HttpDestination')
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

    @property
    def static_dimensions(self) -> dict:
        return self.config.get('properties', {})

    @property
    def flush_bucket_size(self) -> FlushBucketSize:
        return FlushBucketSize(self.config.get(self.FLUSH_BUCKET_SIZE, '1d'))

    @flush_bucket_size.setter
    def flush_bucket_size(self, value: str):
        self.config[self.FLUSH_BUCKET_SIZE] = FlushBucketSize(value).value

    @property
    def static_dimension_names(self):
        return self.static_dimensions.keys()

    @property
    def dimensions(self) -> list:
        dimensions = self.config.get('dimensions')
        if not dimensions:
            return []
        if type(self.config['dimensions']) is dict:
            dimensions = self.required_dimensions + self.optional_dimensions
        return dimensions

    @property
    def required_dimensions(self) -> list:
        dimensions = self.config.get('dimensions')
        if type(dimensions) is not dict or 'required' not in dimensions:
            return []
        return dimensions['required']

    @property
    def optional_dimensions(self) -> list:
        dimensions = self.config.get('dimensions')
        if type(dimensions) is not dict or 'optional' not in dimensions:
            return []
        return dimensions['optional']

    @property
    def dimensions_names(self):
        return [tools.replace_illegal_chars(d.replace('/', '_')) for d in self.dimensions]

    @property
    def dimensions_paths(self):
        return [self.get_property_path(value) for value in self.dimensions]

    @property
    def required_dimensions_paths(self) -> list:
        # todo replace chars
        return [self.get_property_path(value) for value in self.required_dimensions]

    @property
    def timestamp_path(self) -> str:
        return self.get_property_path(self.config['timestamp']['name'])

    @property
    def timezone(self) -> str:
        return self.config.get('timezone', 'UTC')

    @property
    def timestamp_type(self) -> TimestampType:
        return TimestampType(self.config['timestamp']['type'])

    @property
    def timestamp_format(self) -> str:
        return self.config['timestamp'].get('format')

    @property
    def values(self) -> dict:
        return self.config.get('values', {})

    @property
    def value_names(self) -> list:
        return list(self.config.get('values', {}).keys())

    @property
    def values_paths(self):
        return [self.get_property_path(value) for value in self.value_names]

    @property
    def target_types(self) -> list:
        if self.source.type == source.TYPE_INFLUX:
            return [self.config.get('target_type', 'gauge')] * len(self.value_names)
        return list(self.config['values'].values())

    @property
    def measurement_names(self):
        return [tools.replace_illegal_chars(self.config.get('measurement_names', {}).get(key, key)) for key in self.value_names]

    @property
    def measurement_names_paths(self):
        return [self.get_property_path(value) for value in self.measurement_names]

    @property
    def target_types_paths(self):
        return [self.get_property_path(t_type) for t_type in self.target_types]

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
    def query(self, query):
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
        return self.config.get('delay', 0)

    @property
    def batch_size(self) -> str:
        return self.config.get('batch_size', 1000)

    @property
    def uses_schema(self) -> bool:
        return bool(self.config.get('uses_schema'))

    @property
    def histories_batch_size(self) -> str:
        return self.config.get('histories_batch_size', 100)

    @property
    def header_attributes(self):
        return self.config.get('header_attributes', [])

    def get_streamsets_config(self) -> dict:
        return pipeline.manager.create_streamsets_pipeline_config(self)

    def get_id(self) -> str:
        return self.name

    def get_offset(self) -> Optional[str]:
        if self.offset:
            return self.offset.offset
        return None

    def get_streamsets(self) -> Optional[sdc_client.IStreamSets]:
        return self.streamsets

    def set_streamsets(self, streamsets_: StreamSets):
        self.streamsets_id = streamsets_.id
        self.streamsets = streamsets_

    def delete_streamsets(self):
        self.streamsets_id = None
        self.streamsets = None

    def get_schema(self) -> dict:
        return self.schema if self.schema else {}

    def has_schema(self) -> bool:
        return bool(self.schema)

    def get_schema_id(self):
        return self.get_schema().get('id')

    def export(self):
        return {
            **self.config,
            self.OVERRIDE_SOURCE: self.override_source,
            'pipeline_id': self.name,
            'source': self.source.name,
        }

    def to_dict(self):
        return {
            'id': self.name,
            'config': self.config,
            'schema': self.get_schema(),
            'override_source': self.override_source,
            'source': self.source.config,
            'destination': self.destination.config,
        }

    def get_property_path(self, property_value: str) -> str:
        mapping = self.source.config.get('csv_mapping', {})
        for idx, item in mapping.items():
            if item == property_value:
                return str(idx)

        return str(property_value)

    def meta_tags(self) -> dict:
        return {
            'source': ['anodot-agent'],
            'source_host_id': [self.destination.host_id],
            'source_host_name': [HOSTNAME],
            'pipeline_id': [self.name],
            'pipeline_type': [self.source.type]
        }

    def get_tags(self) -> dict:
        return {
            **self.meta_tags(),
            **self.tags
        }

    def error_notification_enabled(self) -> bool:
        return not self.config.get('disable_error_notifications', False)


class TestPipeline(Pipeline):
    def __init__(self, pipeline_id: str, source_, destination: HttpDestination):
        super().__init__(pipeline_id, source_, destination)


class PipelineOffset(Entity):
    __tablename__ = 'pipeline_offsets'

    id = Column(Integer, primary_key=True)
    pipeline_id = Column(Integer, ForeignKey('pipelines.id'))
    offset = Column(String)

    def __init__(self, pipeline_id: int, offset: str):
        self.pipeline_id = pipeline_id
        self.offset = offset


class Provider(sdc_client.IPipelineProvider):
    def get_all(self) -> List[Pipeline]:
        return pipeline.repository.get_all()

    def save(self, pipeline_: Pipeline):
        pipeline.repository.save(pipeline_)


class PipelineRetries(Entity):
    __tablename__ = 'pipeline_retries'

    pipeline_id = Column(String, ForeignKey('pipelines.name'), primary_key=True)
    number_of_error_statuses = Column(Integer)

    def __init__(self, pipeline_: Pipeline):
        self.pipeline_id = pipeline_.name
        self.number_of_error_statuses = 0
