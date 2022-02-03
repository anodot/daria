import requests
import json
import unittest
from agent.modules.constants import ANODOT_API_URL
from agent.pipeline.json_builder.json_builder import _deep_update


class TestDvpConfigDefault(unittest.TestCase):
    def setUp(self) -> None:
        self.dvp_default = {
            'baseRollup': 'MEDIUMROLLUP',
            'maxDVPDurationHours': 24,
            'preventNoData': True,
            'gaugeValue': {'value': 0, 'keepLastValue': False},
            'counterValue': {'value': 0, 'keepLastValue': False},
        }
        self.schema = {
            'id': '1',
            'version': '1',
            'name': 'test_name',
            'dimensions': ['1', '2'],
            'measurements': {'clicks': {'aggregation': 'average', 'countBy': 'none'}},
            'missingDimPolicy': {'action': 'fill', 'fill': 'NULL'},
            'dvpConfig': self.dvp_default
        }
        self.token = 'correct_token'

    def test_default_dvp_01(self):
        config_to_update = {
            'baseRollup': 'MEDIUMROLLUP',
            'maxDVPDurationHours': 1,
            'gaugeValue': {'value': 1, 'keepLastValue': True},
        }
        _deep_update(self.dvp_default, config_to_update)

        assert self.dvp_default == {
            'baseRollup': 'MEDIUMROLLUP',
            'maxDVPDurationHours': 1,
            'preventNoData': True,
            'gaugeValue': {'value': 1, 'keepLastValue': True},
            'counterValue': {'value': 0, 'keepLastValue': False},
        }

    def test_default_dvp_02(self):
        config_to_update = {
            'baseRollup': 'SHORTROLLUP',
            'maxDVPDurationHours': 34,
            'preventNoData': False,
            'gaugeValue': {'value': 500, 'keepLastValue': False},
            'counterValue': {'keepLastValue': True}
        }
        _deep_update(self.dvp_default, config_to_update)

        assert self.dvp_default == {
            'baseRollup': 'SHORTROLLUP',
            'maxDVPDurationHours': 34,
            'preventNoData': False,
            'gaugeValue': {'value': 500, 'keepLastValue': False},
            'counterValue': {'value': 0, 'keepLastValue': True},
        }

    def test_default_dvp_03(self):
        config_to_update = {
            'baseRollup': 'LONGROLLUP',
            'maxDVPDurationHours': 5,
        }
        _deep_update(self.dvp_default, config_to_update)

        assert self.dvp_default == {
            'baseRollup': 'LONGROLLUP',
            'maxDVPDurationHours': 5,
            'preventNoData': True,
            'gaugeValue': {'value': 0, 'keepLastValue': False},
            'counterValue': {'value': 0, 'keepLastValue': False},
        }

    def test_dummy_update_request(self):
        headers = {'Content-Type': 'application/json'}

        pipeline_id = 'test_id'
        self.schema['id'] = pipeline_id
        dvp_config = {
            'baseRollup': 'LONGROLLUP',
            'maxDVPDurationHours': 24
        }
        _deep_update(self.dvp_default, dvp_config)

        assert self.schema['dvpConfig'] == {
            'baseRollup': 'LONGROLLUP',
            'maxDVPDurationHours': 24,
            'preventNoData': True,
            'gaugeValue': {'value': 0, 'keepLastValue': False},
            'counterValue': {'value': 0, 'keepLastValue': False},
        }

        # POST with schema['id'] == id
        url = f'{ANODOT_API_URL}/api/v1/stream-schemas/internal/?token={self.token}&id={pipeline_id}'
        response = requests.request('POST', url, headers=headers, data=json.dumps(self.schema))
        assert response.status_code == 200
        assert response.json()['schema']['id'] == pipeline_id

        # POST with schema['id'] != id
        pipeline_id = 'other-id'
        url = f'{ANODOT_API_URL}/api/v1/stream-schemas/internal/?token={self.token}&id={pipeline_id}'
        response = requests.request('POST', url, headers=headers, data=json.dumps(self.schema))
        assert response.status_code == 200
        assert response.json()['schema']['id'] != pipeline_id
        assert response.json()['schema']['id'] == self.schema['name'] + '-4321'
