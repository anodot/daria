from agent import source
from agent.pipeline.config.stages.base import JythonSource


class SageScript(JythonSource):
    JYTHON_SCRIPT = 'sage.py'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'PIPELINE_NAME',
                'value': self.pipeline.name
            },
            {
                'key': 'SAGE_TOKEN',
                'value': self.pipeline.source.config[source.SageSource.TOKEN]
            },
            {
                'key': 'SAGE_URL',
                'value': self.pipeline.source.config[source.SageSource.URL]
            },
            {
                'key': 'SAGE_SOURCE_HEADER',
                'value': self.pipeline.source.config.get(source.SageSource.SAGE_SOURCE_HEADER, 'anodot')
            },
            {
                'key': 'QUERY',
                'value': self.pipeline.query
            },
            {
                'key': 'INTERVAL',
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
        ]
