
from agent import source
from agent.pipeline.config.stages.base import JythonSource


class PRTGSource(JythonSource):
    JYTHON_SCRIPT = 'prtg.py'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'URL',
                'value': self.pipeline.source.config[source.PRTGSource.URL]
            },
            {
                'key': 'USERNAME',
                'value': self.pipeline.source.config[source.PRTGSource.AUTHENTICATION][source.PRTGSource.USERNAME]
            },
            {
                'key': 'PASSWORD',
                'value': self.pipeline.source.config[source.PRTGSource.AUTHENTICATION][source.PRTGSource.PASSWORD]
            },
            {
                'key': 'VERIFY_SSL',
                'value': '1' if self.pipeline.source.config.get(source.APISource.VERIFY_SSL, True) else ''
            },
            {
                'key': 'INTERVAL_IN_SECONDS',
                'value': str(self.pipeline.interval)
            },
            {
                'key': 'WATERMARK_IN_LOCAL_TIMEZONE',
                'value': str(self.pipeline.watermark_in_local_timezone),
            },
            {
                'key': 'TIMEZONE',
                'value': str(self.pipeline.timezone),
            },
        ]
