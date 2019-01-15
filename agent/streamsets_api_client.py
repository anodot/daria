import requests
import urllib.parse

from logger import get_logger


class StreamSetsApiClient:

    def __init__(self, username, password, base_url='http://localhost:18630'):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({'X-Requested-By': 'sdc'})

        self.logger = get_logger(__name__)

    def build_url(self, *args):
        return urllib.parse.urljoin(self.base_url, '/'.join(['/rest/v1', *args]))

    def create_pipeline(self, name):
        self.logger.info(f'Creating pipeline: {name}')
        res = self.session.put(self.build_url('pipeline', name), params={'autoGeneratePipelineId': 'true'})
        res.raise_for_status()
        return res.json()

    def update_pipeline(self, pipeline_id, pipeline):
        self.logger.info(f'Updating pipeline: {pipeline_id}')
        self.logger.info(f'Pipeline data: {pipeline}')
        res = self.session.post(self.build_url('pipeline', pipeline_id), json=pipeline)
        res.raise_for_status()
        return res.json()

    def update_pipeline_rules(self, pipeline_id, rules):
        self.logger.info(f'Updating pipeline rules: {pipeline_id}')
        self.logger.info(f'Rules data: {rules}')
        res = self.session.post(self.build_url('pipeline', pipeline_id, 'rules'), json=rules)
        res.raise_for_status()
        return res.json()

    def get_pipeline_rules(self, pipeline_id):
        self.logger.info(f'Get pipeline rules: {pipeline_id}')
        res = self.session.get(self.build_url('pipeline', pipeline_id, 'rules'))
        res.raise_for_status()
        return res.json()

    def start_pipeline(self, pipeline_id):
        self.logger.info(f'Start pipeline: {pipeline_id}')
        res = self.session.post(self.build_url('pipeline', pipeline_id, 'start'))
        res.raise_for_status()
        return res.json()

    def stop_pipeline(self, pipeline_id):
        self.logger.info(f'Stop pipeline: {pipeline_id}')
        res = self.session.post(self.build_url('pipeline', pipeline_id, 'stop'))
        res.raise_for_status()
        return res.json()
