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

