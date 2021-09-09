import urllib.parse

from agent import source
from agent.pipeline.config.stages.source import Source


ALLOWED_PORTS_PARAMS = ["location", "device_id", "group", "disable", "deleted", "ignore", "ifSpeed",
                        "ifType", "hostname", "ifAlias", "ifDescr", "port_descr_type", "errors",
                        "alerted", "state", "cbqos", "mac_accounting"]


class ObserviumScript(Source):
    JYTHON_SCRIPT = 'observium.py'

    def get_config(self) -> dict:
        with open(self.get_jython_file_path()) as f:
            script = f.read()
        base_url = urllib.parse.urljoin(
            self.pipeline.source.config[source.ObserviumSource.URL],
            '/api/v0/'
        )
        return {
            'scriptConf.params': [
                {'key': 'DEVICES_URL', 'value': urllib.parse.urljoin(base_url, 'devices')},
                {'key': 'PORTS_URL', 'value': urllib.parse.urljoin(base_url, 'ports')},
                # todo support device params or remove
                # {'key': 'DEVICES_PARAMS', 'value': },
                {'key': 'PORTS_PARAMS', 'value': self._ports_params()},
                {'key': 'MEASUREMENTS', 'value': self.pipeline.config.get('measurements') or _default_measurements()},
                {'key': 'DIMENSIONS', 'value': self.pipeline.dimensions or _default_dimensions()},
                {'key': 'API_USER', 'value': self.pipeline.source.config[source.ObserviumSource.USERNAME]},
                {'key': 'API_PASSWORD', 'value': self.pipeline.source.config[source.ObserviumSource.PASSWORD]},
                {'key': 'INTERVAL_IN_SECONDS', 'value': str(self.pipeline.interval)},
                {'key': 'DELAY_IN_SECONDS', 'value': str(self.pipeline.delay)},
                {'key': 'DAYS_TO_BACKFILL', 'value': self.pipeline.days_to_backfill},
                {'key': 'QUERY_TIMEOUT', 'value': str(self.pipeline.source.query_timeout)},
                {'key': 'VERIFY_SSL', 'value': '1' if self.pipeline.source.config.get('verify_ssl', True) else ''},
                {'key': 'SCHEMA_ID', 'value': self.pipeline.get_schema_id()},
                {'key': 'MONITORING_URL', 'value': self._monitoring_url()},
            ],
            'script': script
        }

    def _monitoring_url(self):
        return urllib.parse.urljoin(
            self.pipeline.streamsets.agent_external_url,
            f'/monitoring/source_http_error/{self.pipeline.name}/'
        )

    def _ports_params(self):
        return {k: v for k, v in self.pipeline.config.get('ports').items() if v and k in ALLOWED_PORTS_PARAMS}


def _default_measurements() -> list:
    return ["encrypted", "ignore", "disabled", "detailed", "deleted", "ifInUcastPkts", "ifInUcastPkts_rate",
            "ifOutUcastPkts", "ifOutUcastPkts_rate", "ifInErrors", "ifInErrors_rate", "ifOutErrors",
            "ifOutErrors_rate", "ifOctets_rate", "ifUcastPkts_rate", "ifErrors_rate", "ifInOctets", "ifInOctets_rate",
            "ifOutOctets", "ifOutOctets_rate", "ifInOctets_perc", "ifOutOctets_perc", "ifInErrors", "ifOutErrors",
            "ifInNUcastPkts", "ifInNUcastPkts_rate", "ifOutNUcastPkts", "ifOutNUcastPkts_rate", "ifInBroadcastPkts",
            "ifInBroadcastPkts_rate", "ifOutBroadcastPkts", "ifOutBroadcastPkts_rate", "ifInMulticastPkts",
            "ifInMulticastPkts_rate", "ifOutMulticastPkts", "ifOutMulticastPkts_rate", "port_mcbc", "ifInDiscards",
            "ifInDiscards_rate", "ifOutDiscards", "ifOutDiscards_rate", "ifDiscards_rate"]


def _default_dimensions() -> list:
    return [
        "ifName",
        "ifAlias",
        "ifDescr",
        "ifSpeed",
        "sysName",
        "location",
    ]
