import pytz
import urllib.parse
from datetime import datetime

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
        body = """{
            "schemaId": "${SCHEMA_ID}",
            "watermark": WATERMARK_EXPRESSION
        }"""
        watermark_expression = "${record:value('/watermark')}"
        if self.pipeline.watermark_in_local_timezone:
            watermark_expression = '${' + self._convert_watermark_to_timezone() + '}'

        body = body.replace('WATERMARK_EXPRESSION', watermark_expression)

        return {
            self.pipeline.destination.CONFIG_ENABLE_REQUEST_LOGGING: self.pipeline.watermark_logs_enabled,
            'conf.requestBody': body,
            **self.pipeline.destination.config,
        }

    def _convert_watermark_to_timezone(self):
        timezone = pytz.timezone(self.pipeline.timezone)
        offset = timezone.utcoffset(datetime.utcnow()).total_seconds()
        return f'record:value("/watermark") - ({int(offset)})'


class EventsDestination(Stage):
    def get_config(self) -> dict:
        return self.pipeline.destination.config


class AnodotEventsDestination(JythonProcessor):
    JYTHON_SCRIPT = 'events_destination.py'

    def _get_script_params(self) -> list[dict]:
        return [{
            'key': 'ANODOT_URL',
            'value': self.pipeline.destination.url
        }, {
            'key': 'ACCESS_TOKEN',
            'value': self.pipeline.destination.access_key
        }, {
            'key': 'PROXIES',
            'value': proxy.get_config(self.pipeline.destination.proxy)
        }, {
            'key': 'AGENT_OFFSET_URL',
            'value': urllib.parse.urljoin(
                self.pipeline.streamsets.agent_external_url, f'/pipeline-offset/{self.pipeline.name}'
            ),
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
