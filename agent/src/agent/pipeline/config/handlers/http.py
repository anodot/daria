from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import TestConfigHandler


class TestHttpConfigHandler(TestConfigHandler):
    stages_to_override = {
        'source': stages.source.http.Http,
    }
