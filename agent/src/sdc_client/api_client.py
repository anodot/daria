import json
import os
import time
import requests
from sdc_client.interfaces import IStreamSets
from sdc_client.base_api_client import (
    _BaseStreamSetsApiClient,
    ApiClientException,
    UnauthorizedException,
    PipelineFreezeException,
)

MAX_TRIES = 3
PREVIEW_TIMEOUT = os.environ.get('STREAMSETS_PREVIEW_TIMEOUT', 30000)


def endpoint(func):
    """
    logs errors and returns json response
    """

    def wrapper(*args, **kwargs):
        for i in range(MAX_TRIES):
            try:
                res = func(*args, **kwargs)
                res.raise_for_status()
                if res.text:
                    return res.json()
            except requests.ConnectionError:
                if i == MAX_TRIES - 1:
                    raise
                continue
            except requests.exceptions.HTTPError:
                if res.text:
                    _parse_error_response(res)
                raise
            return

    return wrapper


def _parse_error_response(result: requests.Response):
    try:
        response = result.json()
    except json.decoder.JSONDecodeError:
        raise ApiClientException(result.text)

    if result.status_code == 401:
        raise UnauthorizedException('Unauthorized')

    raise ApiClientException.raise_from_response(response)


class _StreamSetsApiClient(_BaseStreamSetsApiClient):
    def __init__(self, streamsets_: IStreamSets):
        super().__init__(streamsets_)
        self.session = self._get_session()

    def _get_session(self):
        session = requests.Session()
        session.keep_alive = False
        session.auth = (self.streamsets.get_username(), self.streamsets.get_password())
        session.headers.update({'X-Requested-By': 'sdc'})
        return session

    @endpoint
    def create_pipeline(self, name: str):
        return super().create_pipeline(name)

    @endpoint
    def update_pipeline(self, pipeline_id: str, pipeline_config: dict):
        return super().update_pipeline(pipeline_id, pipeline_config)

    @endpoint
    def start_pipeline(self, pipeline_id: str):
        return super().start_pipeline(pipeline_id)

    @endpoint
    def stop_pipeline(self, pipeline_id: str):
        return super().stop_pipeline(pipeline_id)

    @endpoint
    def force_stop(self, pipeline_id: str):
        return super().force_stop(pipeline_id)

    @endpoint
    def get_pipelines(self, order_by='NAME', order='ASC', label=None):
        return super().get_pipelines(order_by, order, label)

    @endpoint
    def get_pipeline_statuses(self) -> requests.Response:
        return super().get_pipeline_statuses()

    @endpoint
    def delete_pipeline(self, pipeline_id: str):
        return super().delete_pipeline(pipeline_id)

    @endpoint
    def get_pipeline_logs(self, pipeline_id: str, severity: str = None):
        return super().get_pipeline_logs(pipeline_id, severity)

    @endpoint
    def get_pipeline(self, pipeline_id: str):
        return super().get_pipeline(pipeline_id)

    @endpoint
    def get_pipeline_status(self, pipeline_id: str):
        return super().get_pipeline_status(pipeline_id)

    @endpoint
    def get_pipeline_history(self, pipeline_id: str):
        return super().get_pipeline_history(pipeline_id)

    @endpoint
    def get_pipeline_metrics(self, pipeline_id: str):
        return super().get_pipeline_metrics(pipeline_id)

    @endpoint
    def reset_pipeline(self, pipeline_id: str):
        return super().reset_pipeline(pipeline_id)

    @endpoint
    def get_pipeline_offset(self, pipeline_id: str):
        return super().get_pipeline_offset(pipeline_id)

    @endpoint
    def post_pipeline_offset(self, pipeline_id: str, offset: dict):
        return super().post_pipeline_offset(pipeline_id, offset)

    @endpoint
    def validate(self, pipeline_id: str):
        return super().validate(pipeline_id)

    @endpoint
    def create_preview(self, pipeline_id: str):
        return super().create_preview(pipeline_id)

    @endpoint
    def get_preview(self, pipeline_id: str, previewer_id: str):
        return super().get_preview(pipeline_id, previewer_id)

    @endpoint
    def get_preview_status(self, pipeline_id: str, previewer_id: str):
        return super().get_preview_status(pipeline_id, previewer_id)

    @endpoint
    def system_stats(self):
        return super().system_stats()

    def wait_for_preview(self, pipeline_id: str, preview_id: str) -> (list, list):
        tries = 6
        initial_delay = 2
        for i in range(1, tries + 1):
            response = self.get_preview_status(pipeline_id, preview_id)
            if response['status'] == 'TIMED_OUT':
                raise ApiClientException(f'No data. Connection timed out')

            # todo constants
            if response['status'] not in [
                'VALIDATING', 'CREATED', 'RUNNING', 'STARTING', 'FINISHING', 'CANCELLING', 'TIMING_OUT'
            ]:
                break

            delay = initial_delay ** i
            if i == tries:
                return [], []
            self.logger.info(f'Waiting for data. Check again after {delay} seconds...')
            time.sleep(delay)

        preview_data = self.get_preview(pipeline_id, preview_id)

        errors = []
        if preview_data['status'] == 'RUN_ERROR':
            errors.append(preview_data['message'])
        if preview_data['issues']:
            for stage, data in preview_data['issues']['stageIssues'].items():
                for issue in data:
                    errors.append(issue['message'])
            for issue in preview_data['issues']['pipelineIssues']:
                errors.append(issue['message'])

        if preview_data['batchesOutput']:
            for batch in preview_data['batchesOutput']:
                for stage in batch:
                    if stage['errorRecords']:
                        for record in stage['errorRecords']:
                            errors.append(record['header']['errorMessage'])

        return preview_data, errors

    @endpoint
    def get_pipeline_errors(self, pipeline_id: str, stage_name):
        return super().get_pipeline_errors(pipeline_id, stage_name)

    @endpoint
    def get_jmx(self, query: str):
        return super().get_jmx(query)

    def wait_for_status(self, pipeline_id: str, status: str):
        tries = 5
        initial_delay = 2
        for i in range(1, tries + 1):
            response = self.get_pipeline_status(pipeline_id)
            if response['status'] == status:
                return True
            delay = initial_delay ** i
            if i == tries:
                raise PipelineFreezeException(
                    f"Pipeline `{pipeline_id}` is still {response['status']} after {tries} tries"
                )
            self.logger.info(f"Pipeline `{pipeline_id}` is {response['status']}. Check again after {delay} seconds...")
            time.sleep(delay)
