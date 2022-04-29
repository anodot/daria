import urllib.parse

from agent.destination import anodot_api_client
from agent.modules import proxy
from .base import Stage, JythonProcessor


class Destination(Stage):
    def get_config(self) -> dict:
        return {
            'conf.agentOffsetUrl': urllib.parse.urljoin(
                self.pipeline.streamsets.agent_external_url, f'/pipeline-offset/{self.pipeline.name}'
            ),
            self.pipeline.destination.CONFIG_ENABLE_REQUEST_LOGGING: self.pipeline.destination.if_logs_enabled,
            **self.pipeline.destination.config,
        }


class WatermarkDestination(Stage):
    def get_config(self) -> dict:
        return {
            'conf.agentWatermarkUrl': urllib.parse.urljoin(
                self.pipeline.streamsets.agent_external_url, f'/pipeline-watermark/{self.pipeline.name}'
            ),
            **self.pipeline.destination.config,
        }


class EventsDestination(Stage):
    def get_config(self) -> dict:
        return self.pipeline.destination.config


class AnodotEventsDestination(JythonProcessor):
    JYTHON_SCRIPT = 'events_destination.py'

    def _get_script_params(self) -> list[dict]:
        client = anodot_api_client.AnodotApiClient(self.pipeline.destination)
        return [{
            'key': 'EVENTS_URL',
            'value': client.get_events_url()
        }, {
            'key': 'REFRESH_TOKEN_URL',
            'value': client.get_refresh_token_url()
        }, {
            'key': 'ACCESS_TOKEN',
            'value': self.pipeline.destination.access_key
        }, {
            'key': 'PROXIES',
            'value': proxy.get_config(self.pipeline.destination.proxy)
        }]


class HttpDestination(Stage):
    def get_config(self) -> dict:
        send_data_format = self.pipeline.config.get('send_data_format', 'DELIMITED')
        config = {
            'conf.dataFormat': send_data_format,
        }
        if send_data_format == 'DELIMITED':
            config['conf.dataGeneratorFormatConfig.csvHeader'] = 'WITH_HEADER'
        return config
