import requests
import urllib.parse


class StreamSetsApiClient:

    def __init__(self, username, password, base_url='http://localhost:18630'):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({'X-Requested-By': 'sdc'})

    def build_url(self, *args):
        return urllib.parse.urljoin(self.base_url, '/'.join(['/rest/v1', *args]))

    def create_pipeline(self, name):
        res = self.session.put(self.build_url('pipeline', name), params={'autoGeneratePipelineId': 'true'})
        res.raise_for_status()
        return res.json()

    def update_pipeline(self, pipeline_id, pipeline):
        res = self.session.post(self.build_url('pipeline', pipeline_id), json=pipeline)
        res.raise_for_status()
        return res.json()

    def update_pipeline_rules(self, pipeline_id, rules):
        res = self.session.post(self.build_url('pipeline', pipeline_id, 'rules'), json=rules)
        res.raise_for_status()
        return res.json()

    def get_pipeline_rules(self, pipeline_id):
        res = self.session.get(self.build_url('pipeline', pipeline_id, 'rules'))
        res.raise_for_status()
        return res.json()

    def start_pipeline(self, pipeline_id):
        res = self.session.post(self.build_url('pipeline', pipeline_id, 'start'))
        res.raise_for_status()
        return res.json()

    def stop_pipeline(self, pipeline_id):
        res = self.session.post(self.build_url('pipeline', pipeline_id, 'stop'))
        res.raise_for_status()
        return res.json()
