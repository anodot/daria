import click
import json
import os
import time

from .. import source
from agent.constants import DATA_DIR
from agent.destination import HttpDestination
from agent.streamsets_api_client import api_client


class Pipeline:
    DIR = os.path.join(DATA_DIR, 'pipelines')
    STATUS_RUNNING = 'RUNNING'
    STATUS_STOPPED = 'STOPPED'
    STATUS_STOPPING = 'STOPPING'

    def __init__(self, pipeline_id: str,
                 source_obj: source.Source,
                 config: dict,
                 destination: HttpDestination):
        self.id = pipeline_id
        self.config = config
        self.source = source_obj
        self.destination = destination

    @property
    def file_path(self) -> str:
        return self.get_file_path(self.id)

    def to_dict(self):
        return {
            **self.config,
            'pipeline_id': self.id,
            'source': self.source.to_dict() if self.source else None,
            'destination': self.destination.to_dict()
        }

    @classmethod
    def get_file_path(cls, pipeline_id: str) -> str:
        return os.path.join(cls.DIR, pipeline_id + '.json')

    @classmethod
    def exists(cls, pipeline_id: str) -> bool:
        return os.path.isfile(cls.get_file_path(pipeline_id))

    def set_config(self, config: dict):
        self.config.update(config)

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.to_dict(), f)

    def check_status(self, status):
        response = api_client.get_pipeline_status(self.id)
        return response['status'] == status

    def wait_for_status(self, status, tries=5, initial_delay=3):
        for i in range(1, tries + 1):
            response = api_client.get_pipeline_status(self.id)
            if response['status'] == status:
                return True
            delay = initial_delay ** i
            if i == tries:
                raise PipelineFreezeException(f"Pipeline {self.id} is still {response['status']} after {tries} tries")
            print(f"Pipeline {self.id} is {response['status']}. Check again after {delay} seconds...")
            time.sleep(delay)

    def wait_for_sending_data(self, tries=5, initial_delay=2):
        for i in range(1, tries + 1):
            response = api_client.get_pipeline_metrics(self.id)
            stats = {
                'in': response['counters']['pipeline.batchInputRecords.counter']['count'],
                'out': response['counters']['pipeline.batchOutputRecords.counter']['count'],
                'errors': response['counters']['pipeline.batchErrorRecords.counter']['count'],
            }
            if stats['out'] > 0 and stats['errors'] == 0:
                return True
            if stats['errors'] > 0:
                raise PipelineException(f"Pipeline {self.id} is has {stats['errors']} errors")
            delay = initial_delay ** i
            if i == tries:
                raise PipelineException(f"Pipeline {self.id} did not send any data. Received number of records - {stats['in']}")
            print(f'Waiting for pipeline {self.id} to send data. Check again after {delay} seconds...')
            time.sleep(delay)

    def stop(self):
        api_client.stop_pipeline(self.id)
        try:
            self.wait_for_status(self.STATUS_STOPPED)
        except PipelineFreezeException:
            print("Force stopping the pipeline")
            self.force_stop()

    def force_stop(self):
        if not self.check_status(self.STATUS_STOPPING):
            raise PipelineException("Can't force stop a pipeline not in the STOPPING state")

        api_client.force_stop_pipeline(self.id)
        self.wait_for_status(self.STATUS_STOPPED)

    def start(self):
        api_client.start_pipeline(self.id)
        self.wait_for_status(self.STATUS_RUNNING)


class PipelineException(click.ClickException):
    pass


class PipelineNotExistsException(PipelineException):
    pass


class PipelineFreezeException(PipelineException):
    pass
