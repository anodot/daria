from agent.pipeline.config.stages.base import JythonDataExtractorSource


class TopologyScript(JythonDataExtractorSource):
    JYTHON_SCRIPT = 'topology.py'
    DATA_EXTRACTOR_API_ENDPOINT = 'topology'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'TOPOLOGY_SOURCE_URL',
                'value': self._get_source_url()
            },
            # todo doesn't interval depend on the source in this case?
            {
                'key': 'INTERVAL_IN_SECONDS',
                'value': str(self.pipeline.interval)
            },
            {
                'key': 'DELAY_IN_MINUTES',
                'value': str(self.pipeline.delay)
            },
        ]
