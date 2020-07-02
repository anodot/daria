import json
import os
import requests
import time
import urllib.parse
import click

from .logger import get_logger
from agent.constants import STREAMSETS_PREVIEW_TIMEOUT

logger = get_logger(__name__)


def endpoint(func):
    """
    Decorator for api endpoints. Logs errors and returns json response

    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        try:
            res.raise_for_status()
            if res.text:
                return res.json()
            return
        except requests.exceptions.HTTPError:
            if res.text:
                try:
                    response = res.json()
                    logger.exception(response['RemoteException'])
                    raise StreamSetsApiClientException(response['RemoteException']['message'])
                except json.decoder.JSONDecodeError:
                    raise StreamSetsApiClientException(res.text)
            raise

    return wrapper


class StreamSetsApiClientException(click.ClickException):
    pass


class StreamSetsApiClient:

    def __init__(self, username, password, base_url='http://localhost:18630'):
        """

        :param username: string
        :param password: string
        :param base_url: string
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({'X-Requested-By': 'sdc'})

    def build_url(self, *args):
        """
        Build url for endpoints
        :param args:
        :return: string
        """
        return urllib.parse.urljoin(self.base_url, '/'.join(['/rest/v1', *args]))

    @endpoint
    def create_pipeline(self, name):
        """

        :param name: string
        :return:
        """
        logger.info(f'Creating pipeline: {name}')
        return self.session.put(self.build_url('pipeline', name))

    @endpoint
    def update_pipeline(self, pipeline_id, pipeline):
        """

        :param pipeline_id: string
        :param pipeline: dict - pipeline config object
        :return:
        """
        logger.info(f'Updating pipeline: {pipeline_id}')
        logger.info(f'Pipeline data: {pipeline}')
        return self.session.post(self.build_url('pipeline', pipeline_id), json=pipeline)

    @endpoint
    def update_pipeline_rules(self, pipeline_id, rules):
        """

        :param pipeline_id: string
        :param rules: dict - pipeline rules object
        :return:
        """
        logger.info(f'Updating pipeline rules: {pipeline_id}')
        logger.info(f'Rules data: {rules}')
        return self.session.post(self.build_url('pipeline', pipeline_id, 'rules'), json=rules)

    @endpoint
    def get_pipeline_rules(self, pipeline_id):
        """

        :param pipeline_id: string
        :return:
        """
        logger.info(f'Get pipeline rules: {pipeline_id}')
        return self.session.get(self.build_url('pipeline', pipeline_id, 'rules'))

    @endpoint
    def start_pipeline(self, pipeline_id):
        """

        :param pipeline_id: string
        :return:
        """
        logger.info(f'Start pipeline: {pipeline_id}')
        return self.session.post(self.build_url('pipeline', pipeline_id, 'start'))

    @endpoint
    def stop_pipeline(self, pipeline_id):
        """

        :param pipeline_id: string
        :return:
        """
        logger.info(f'Stop pipeline: {pipeline_id}')
        return self.session.post(self.build_url('pipeline', pipeline_id, 'stop'))

    @endpoint
    def force_stop_pipeline(self, pipeline_id):
        """

        :param pipeline_id: string
        :return:
        """
        logger.info(f'Force stop pipeline: {pipeline_id}')
        return self.session.post(self.build_url('pipeline', pipeline_id, 'forceStop'))

    @endpoint
    def get_pipelines(self, order_by='NAME', order='ASC', label=None):
        logger.info('Get pipelines')
        params = {'orderBy': order_by, 'order': order}
        if label:
            params['label'] = label
        return self.session.get(self.build_url('pipelines'), params=params)\


    @endpoint
    def get_pipeline(self, pipeline_id: str):
        logger.info('Get pipelines')
        params = {'pipelineId': pipeline_id}
        return self.session.get(self.build_url('pipelines'), params=params)

    @endpoint
    def get_pipelines_status(self):
        logger.info('Get pipelines status')
        return self.session.get(self.build_url('pipelines', 'status'))

    @endpoint
    def get_pipeline_status(self, pipeline_id: str):
        logger.info(f'Get pipeline {pipeline_id} status')
        return self.session.get(self.build_url('pipelines', 'status', {'pipelineId': pipeline_id}))

    @endpoint
    def delete_pipeline(self, pipeline_id):
        """

        :param pipeline_id: string
        :return:
        """
        logger.info(f'Delete pipeline: {pipeline_id}')
        return self.session.delete(self.build_url('pipeline', pipeline_id))

    @endpoint
    def get_pipeline_logs(self, pipeline_id, level=None):
        """
        :param pipeline_id: string
        :param level: string [INFO, ERROR], default - None
        :return:
        """
        logger.info(f'Get pipeline logs: {pipeline_id}, logging level:{level}')
        params = {'pipeline': pipeline_id, 'endingOffset': -1}
        if level:
            params['level'] = level
        return self.session.get(self.build_url('system', 'logs'), params=params)

    @endpoint
    def get_pipeline(self, pipeline_id):
        """

        :param pipeline_id: string
        :return:
        """
        logger.info(f'Get pipeline {pipeline_id}')
        return self.session.get(self.build_url('pipeline', pipeline_id))

    @endpoint
    def get_pipeline_status(self, pipeline_id):
        """

        :param pipeline_id: string
        :return:
        """
        logger.info(f'Get pipeline status {pipeline_id}')
        return self.session.get(self.build_url('pipeline', pipeline_id, 'status'))

    @endpoint
    def get_pipeline_history(self, pipeline_id):
        """

        :param pipeline_id: string
        :return:
        """
        logger.info(f'Get pipeline history {pipeline_id}')
        return self.session.get(self.build_url('pipeline', pipeline_id, 'history'))

    @endpoint
    def get_pipeline_metrics(self, pipeline_id):
        """

        :param pipeline_id: string
        :return:
        """
        logger.info(f'Get pipeline metrics {pipeline_id}')
        return self.session.get(self.build_url('pipeline', pipeline_id, 'metrics'))

    @endpoint
    def reset_pipeline(self, pipeline_id):
        """

        :param pipeline_id: string
        :return:
        """
        logger.info(f'Reset pipeline offset {pipeline_id}')
        return self.session.post(self.build_url('pipeline', pipeline_id, 'resetOffset'))

    @endpoint
    def delete_by_filtering(self, filter_text):
        """

        :param filter_text: string
        :return:
        """
        logger.info(f'Delete pipelines with text: {filter_text}')
        return self.session.post(self.build_url('pipelines', 'deleteByFiltering'), params={'filterText': filter_text})

    @endpoint
    def validate(self, pipeline_id: str):
        logger.info(f'Validate pipeline {pipeline_id}')
        return self.session.get(self.build_url('pipeline', pipeline_id, 'validate'),
                                params={'timeout': STREAMSETS_PREVIEW_TIMEOUT})

    @endpoint
    def create_preview(self, pipeline_id: str):
        logger.info(f'Create pipeline {pipeline_id} preview')
        return self.session.post(self.build_url('pipeline', pipeline_id, 'preview'),
                                 params={'timeout': STREAMSETS_PREVIEW_TIMEOUT})

    @endpoint
    def get_preview(self, pipeline_id: str, previewer_id: str):
        logger.info(f'Validate pipeline {pipeline_id}')
        return self.session.get(self.build_url('pipeline', pipeline_id, 'preview', previewer_id))

    @endpoint
    def get_preview_status(self, pipeline_id: str, previewer_id: str):
        logger.info(f'Validate pipeline {pipeline_id}')
        return self.session.get(self.build_url('pipeline', pipeline_id, 'preview', previewer_id, 'status'))

    def wait_for_preview(self, pipeline_id, preview_id, tries=6, initial_delay=2):
        for i in range(1, tries + 1):
            response = self.get_preview_status(pipeline_id, preview_id)
            if response['status'] == 'TIMED_OUT':
                raise StreamSetsApiClientException(f"No data. Connection timed out")

            if response['status'] not in ['VALIDATING', 'CREATED', 'RUNNING', 'STARTING', 'FINISHING', 'CANCELLING',
                                          'TIMING_OUT']:
                break

            delay = initial_delay ** i
            if i == tries:
                raise StreamSetsApiClientException(f"No data")
            print(f"Waiting for data. Check again after {delay} seconds...")
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

        if errors:
            raise StreamSetsApiClientException('\n'.join(errors))

        return preview_data

    @endpoint
    def get_pipeline_errors(self, pipeline_id, stage_name):
        logger.info(f'Get pipeline {pipeline_id} errors')
        return self.session.get(self.build_url('pipeline', pipeline_id, 'errorRecords'),
                                params={'stageInstanceName': stage_name})


api_client = StreamSetsApiClient(os.environ.get('STREAMSETS_USERNAME', 'admin'),
                                 os.environ.get('STREAMSETS_PASSWORD', 'admin'),
                                 os.environ.get('STREAMSETS_URL', 'http://localhost:18630'))
