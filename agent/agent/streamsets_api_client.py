import requests
import urllib.parse

from .logger import get_logger

logger = get_logger(__name__)


def endpoint(func):
    """
    Decorator for api endpoints. Logs errors and returns json response

    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            res.raise_for_status()
            if res.text:
                return res.json()
            return
        except Exception:
            logger.exception('Exception')
            raise

    return wrapper


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
        return self.session.put(self.build_url('pipeline', name), params={'autoGeneratePipelineId': 'true'})

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
    def get_pipelines(self):
        logger.info('Get pipelines')
        return self.session.get(self.build_url('pipelines'))

    @endpoint
    def get_pipelines_status(self):
        logger.info('Get pipelines status')
        return self.session.get(self.build_url('pipelines', 'status'))

    @endpoint
    def delete_pipeline(self, pipeline_id):
        """

        :param pipeline_id: string
        :return:
        """
        logger.info(f'Delete pipeline: {pipeline_id}')
        return self.session.delete(self.build_url('pipeline', pipeline_id))

    @endpoint
    def get_pipeline_logs(self, pipeline_id, severity=None):
        """

        :param pipeline_id: string
        :param severity: string [INFO, ERROR], default - None
        :return:
        """
        logger.info(f'Get pipeline logs: {pipeline_id}, severity:{severity}')
        params = {'pipeline': pipeline_id, 'endingOffset': -1}
        if severity:
            params['severity'] = severity
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
