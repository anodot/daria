import unittest
from agent.modules.tools import deep_update


class TestDeepUpdate(unittest.TestCase):
    def setUp(self) -> None:
        self.dvp_config = {
            'baseRollup': 'MEDIUMROLLUP',
            'maxDVPDurationHours': 24,
            'preventNoData': True,
            'gaugeValue': {'value': 0, 'keepLastValue': False},
            'counterValue': {'value': 0, 'keepLastValue': False},
        }

    def test_default_dvp_01(self):
        src_dvp = {
            'baseRollup': 'LONGROLLUP',
            'maxDVPDurationHours': 1,
            'gaugeValue': {'value': 1, 'keepLastValue': True},
        }
        deep_update(src_dvp, self.dvp_config)

        assert self.dvp_config == {
            'baseRollup': 'LONGROLLUP',
            'maxDVPDurationHours': 1,
            'preventNoData': True,
            'gaugeValue': {'value': 1, 'keepLastValue': True},
            'counterValue': {'value': 0, 'keepLastValue': False},
        }

    def test_default_dvp_02(self):
        src_dvp = {
            'baseRollup': 'SHORTROLLUP',
            'maxDVPDurationHours': 34,
            'preventNoData': False,
            'gaugeValue': {'value': 500, 'keepLastValue': False},
            'counterValue': {'keepLastValue': True}
        }
        deep_update(src_dvp, self.dvp_config)

        assert self.dvp_config == {
            'baseRollup': 'SHORTROLLUP',
            'maxDVPDurationHours': 34,
            'preventNoData': False,
            'gaugeValue': {'value': 500, 'keepLastValue': False},
            'counterValue': {'value': 0, 'keepLastValue': True},
        }

    def test_default_dvp_03(self):
        src_dvp = {
            'baseRollup': 'LONGROLLUP',
            'maxDVPDurationHours': 5,
        }
        deep_update(src_dvp, self.dvp_config)

        assert self.dvp_config == {
            'baseRollup': 'LONGROLLUP',
            'maxDVPDurationHours': 5,
            'preventNoData': True,
            'gaugeValue': {'value': 0, 'keepLastValue': False},
            'counterValue': {'value': 0, 'keepLastValue': False},
        }

    def test_default_dvp_04(self):
        src_dvp = {}
        deep_update(src_dvp, self.dvp_config)

        assert self.dvp_config == {
            'baseRollup': 'MEDIUMROLLUP',
            'maxDVPDurationHours': 24,
            'preventNoData': True,
            'gaugeValue': {'value': 0, 'keepLastValue': False},
            'counterValue': {'value': 0, 'keepLastValue': False},
        }

    def test_generic_01(self):
        src_dict = {
            'key_1': 'value_1',
            'key_2': 'value_2',
            'inner_1': {
                '1': 'a',
                '2': 'b',
            }
        }
        dst_dict = {}
        deep_update(src_dict, dst_dict)
        assert src_dict == dst_dict

    def test_generic_02(self):
        src_dict = {
            'key_1': 'value_1',
            'key_2': 'value_2',
            'inner_1': {
                '1': 'a',
                '2': 'b',
            }
        }
        dst_dict = {'key_1': 'default_value_1', 'key_2': 'default_value_2'}
        deep_update(src_dict, dst_dict)
        assert src_dict == dst_dict
