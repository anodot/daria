import urllib.parse

from agent.pipeline.config.stages.base import JythonProcessor


class TopologyScript(JythonProcessor):
    JYTHON_SCRIPT = 'topology/transform.py'
    DATA_EXTRACTOR_API_ENDPOINT = 'data_extractors/topology'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'TOPOLOGY_TRANSFORM_RECORDS_URL',
                'value': self._get_source_url(),
            },
        ]

    def _get_source_url(self) -> str:
        return urllib.parse.urljoin(
            self.pipeline.streamsets.agent_external_url, '/'.join([
                self.DATA_EXTRACTOR_API_ENDPOINT,
                '${pipeline:id()}',
            ])
        )


class DirectoryCsvToJson(JythonProcessor):
    JYTHON_SCRIPT = 'topology/csv_to_json.py'

    def _get_script_params(self) -> list[dict]:
        return []
