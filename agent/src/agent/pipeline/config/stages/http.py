import urllib.parse

from .base import Stage


class SendFileProcessedMetric(Stage):
    def get_config(self) -> dict:
        agent_url = self.pipeline.streamsets.agent_external_url
        return {
            'conf.resourceUrl': urllib.parse.urljoin(
                agent_url, f'/monitoring/directory_file_processed/{self.pipeline.name}'
            ),
        }


class SendWatermark(Stage):
    def get_config(self) -> dict:
        agent_url = self.pipeline.streamsets.agent_external_url
        return {
            'conf.resourceUrl': urllib.parse.urljoin(
                agent_url, f'/pipelines/{self.pipeline.name}/send-watermark'
            ),
        }
