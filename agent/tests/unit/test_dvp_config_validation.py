import unittest
from unittest.mock import MagicMock

from agent.pipeline import Pipeline
from agent.pipeline.json_builder import Builder
from jsonschema import ValidationError


class TestDvpConfigValidation(unittest.TestCase):
    pipeline_ = MagicMock(spec=Pipeline)

    def test_dvp_config_validate_OK(self):
        config = {
            "dvpConfig": {
                "baseRollup": "LONGROLLUP",
                "maxDVPDurationHours": 24,
                "gaugeValue": {"keepLastValue": True},
                "counterValue": {"value": 0}
            }
        }
        builder = Builder(self.pipeline_, config, False)
        self.assertIsNone(builder._validate_dvp_config_json_schema())

    def test_dvp_config_ok_SHORTROLLUP(self):
        config = {
            "dvpConfig": {
                "baseRollup": "SHORTROLLUP",
                "maxDVPDurationHours": 24,
                "gaugeValue": {"keepLastValue": True},
                "counterValue": {"value": 5}
            }
        }
        builder = Builder(self.pipeline_, config, False)
        self.assertIsNone(builder._validate_dvp_config_json_schema())

    def test_dvp_config_fail_maxDVPDurationHours(self):
        config = {
            "dvpConfig": {
                "baseRollup": "LONGLONGROLLUP",
                "maxDVPDurationHours": 1000,
                "gaugeValue": {"keepLastValue": True},
                "counterValue": {"value": 5}
            }
        }
        builder = Builder(self.pipeline_, config, False)
        with self.assertRaises(ValidationError):
            builder._validate_dvp_config_json_schema()

    def test_dvp_config_fail_no_baseRollup(self):
        config = {
            "dvpConfig": {
                "maxDVPDurationHours": 24,
            }
        }
        builder = Builder(self.pipeline_, config, False)
        with self.assertRaises(ValidationError):
            builder._validate_dvp_config_json_schema()

    def test_dvp_config_fail_no_maxDVPDurationHours(self):
        config = {
            "dvpConfig": {
                "baseRollup": "LONGROLLUP",
            }
        }
        builder = Builder(self.pipeline_, config, False)
        with self.assertRaises(ValidationError):
            builder._validate_dvp_config_json_schema()

    def test_dvp_config_fail_gaugeValue_inner(self):
        config = {
            "dvpConfig": {
                "baseRollup": "LONGROLLUP",
                "maxDVPDurationHours": 24,
                "gaugeValue": {
                    "wrong_property": "test"
                }
            }
        }
        builder = Builder(self.pipeline_, config, False)
        with self.assertRaises(ValidationError):
            builder._validate_dvp_config_json_schema()

    def test_dvp_config_fail_counterValue_inner_value(self):
        config = {
            "dvpConfig": {
                "baseRollup": "LONGROLLUP",
                "maxDVPDurationHours": 10,
                "gaugeValue": {
                    "counterValue": {
                        "value": "str"
                    }
                }
            }
        }
        builder = Builder(self.pipeline_, config, False)
        with self.assertRaises(ValidationError):
            builder._validate_dvp_config_json_schema()
