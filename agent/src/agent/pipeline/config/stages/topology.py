from agent.pipeline.config.stages.base import JythonProcessor


class TopologyScript(JythonProcessor):
    JYTHON_SCRIPT = 'topology/transform.py'
    DATA_EXTRACTOR_API_ENDPOINT = 'data_extractors/topology'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'INTERVAL_IN_SECONDS',
                'value': str(self.pipeline.interval)
            },
            {
                'key': 'DELAY_IN_MINUTES',
                'value': str(self.pipeline.delay)
            },
        ]
