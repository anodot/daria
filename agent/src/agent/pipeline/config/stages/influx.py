from .base import JythonSource, JythonProcessor
from datetime import datetime, timedelta


class InfluxScript(JythonSource):
    JYTHON_SCRIPT = 'influx.py'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'INITIAL_OFFSET',
                'value': self._get_offset()
            },
            {
                'key': 'INTERVAL_IN_SECONDS',
                'value': str(self.pipeline.config.get('interval', ''))
            },
            {
                'key': 'DELAY_IN_SECONDS',
                'value': str(_convert_to_seconds(self.pipeline.config.get('delay', '0s')))
            },
        ]

    def _get_offset(self) -> str:
        offset = self.pipeline.source.config.get('offset', '')
        # if it's a digit - then offset is in number of days
        if offset.isdigit():
            offset = (datetime.now() - timedelta(days=int(offset))).strftime('%d/%m/%Y %H:%M')
        return offset


class JythonTransformRecords(JythonProcessor):
    JYTHON_SCRIPT = 'influx2_transform_records.py'

    def _get_script_params(self) -> list[dict]:
        return [
            {'key': 'TIMESTAMP_COLUMN', 'value': self.pipeline.config['timestamp']['name']},
            {'key': 'VARIABLES', 'value': self.pipeline.config.get('variables', [])},
        ]


def _convert_to_seconds(string):
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    return int(string[:-1]) * seconds_per_unit[string[-1]]
