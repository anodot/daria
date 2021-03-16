from agent.pipeline.config.stages.base import Stage


class Cacti(Stage):
    JYTHON_SCRIPT = 'cacti.py'

    def _get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            return {
                'scriptConf.params': [
                    {'key': 'RRD_SOURCE_URL', 'value': self._get_rrd_source_url()},
                    {'key': 'INTERVAL_IN_SECONDS', 'value': str(self.pipeline.interval)},
                    {'key': 'DELAY_IN_MINUTES', 'value': str(self.pipeline.delay)},
                    {'key': 'DAYS_TO_BACKFILL', 'value': str(self.pipeline.days_to_backfill)},
                ],
                'script': f.read(),
            }

    def _get_rrd_source_url(self) -> str:
        return self.pipeline.streamsets.agent_external_url + '/rrd_source/fetch_data/${pipeline:id()}'