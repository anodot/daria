from .base import BaseConfigHandler
from ..prompt import PromptConfigInflux
from agent.logger import get_logger

logger = get_logger(__name__)


class InfluxConfigHandler(BaseConfigHandler):
    def override_base_config(self, new_uuid=None, new_pipeline_title=None):
        pass

    def override_base_rules(self, new_uuid):
        pass
