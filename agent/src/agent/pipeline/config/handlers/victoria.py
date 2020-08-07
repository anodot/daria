import os

from agent import pipeline
from agent.constants import ROOT_DIR
from .base import BaseConfigHandler
from agent.logger import get_logger
from agent.pipeline.config import stages

logger = get_logger(__name__)


class VictoriaConfigHandler(BaseConfigHandler):
    PIPELINE_BASE_CONFIG_NAME = 'victoria_http.json'
    JYTHON_SCRIPT = 'victoria.py'

    stages = {
        'source': stages.victoria_source.VictoriaScript,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties,
        'destination': stages.destination.Destination
    }

    def load_base_config(self):
        config = super().load_base_config()
        with open(os.path.join(ROOT_DIR, self.JYTHON_SCRIPTS_PATH, self.JYTHON_SCRIPT)) as f:
            config['stages'][0]['configuration'][0]['value'] = f.read()
        return config

    def override_stages(self):
        self.pipeline.config['timestamp'] = {
            'type': pipeline.TimestampType.UNIX.value
        }
        super().override_stages()
