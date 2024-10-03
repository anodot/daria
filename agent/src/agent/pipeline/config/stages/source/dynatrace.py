from agent import monitoring, source
from agent.pipeline.config.stages.base import JythonSource


class DynatraceScript(JythonSource):
    JYTHON_SCRIPT = 'dynatrace.py'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'PIPELINE_NAME',
                'value': self.pipeline.name
            },
            {
                'key': 'DYNATRACE_TOKEN',
                'value': self.pipeline.source.config[source.SageSource.TOKEN]
            },
            {
                'key': 'DYNATRACE_URL',
                'value': self.pipeline.source.config[source.SageSource.URL]
            },
            {
                'key': 'INTERVAL_IN_MINUTES',
                'value': str(self.pipeline.interval)
            },
            {
                'key': 'DELAY',
                'value': str(self.pipeline.delay)
            },
            {
                'key': 'DAYS_TO_BACKFILL',
                'value': self.pipeline.days_to_backfill
            },
            {
                'key': 'QUERY_SIZE',
                'value': str(self.pipeline.batch_size)
            },
            {
                'key': 'DVP_ENABLED',
                'value': str(bool(self.pipeline.dvp_config))
            },
            {
                'key': 'MONITORING_URL',
                'value': monitoring.get_monitoring_source_error_url(self.pipeline)
            },
        ]
