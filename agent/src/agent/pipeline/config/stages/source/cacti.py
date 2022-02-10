from agent.pipeline.config.stages.base import JythonDataExtractorSource


class Cacti(JythonDataExtractorSource):
    JYTHON_SCRIPT = 'cacti.py'
    DATA_EXTRACTOR_API_ENDPOINT = 'data_extractor/cacti'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'RRD_SOURCE_URL',
                'value': self._get_source_url()
            },
            {
                'key': 'INTERVAL_IN_SECONDS',
                'value': str(self.pipeline.interval)
            },
            {
                'key': 'DELAY_IN_MINUTES',
                'value': str(self.pipeline.delay)
            },
            {
                'key': 'DAYS_TO_BACKFILL',
                'value': str(self.pipeline.days_to_backfill)
            },
            {
                'key': 'STEP_IN_SECONDS',
                # we need 'or interval' for the case when the step is dynamic
                'value': str(self.pipeline.config.get('step') or self.pipeline.interval)
            },
        ]
