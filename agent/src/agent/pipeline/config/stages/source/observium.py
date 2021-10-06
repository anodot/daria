import urllib.parse

from agent import source
from agent.pipeline.config.stages.source import Source

PORTS = 'ports'
MEMPOOLS = 'mempools'
PROCESSORS = 'processors'
STORAGE = 'storage'

ALLOWED_PARAMS = {
    PORTS: ["location", "device_id", "group", "disable", "deleted", "ignore", "ifSpeed", "ifType", "hostname",
            "ifAlias", "ifDescr", "port_descr_type", "errors", "alerted", "state", "cbqos", "mac_accounting"],
    MEMPOOLS: ["group_id", "device_id", "mempool_descr"],
    PROCESSORS: ["group_id", "device_id", "processor_descr"],
    STORAGE: ["group_id", "device_id", "storage_descr"],
}

DEFAULT_MEASUREMENTS = {
    PORTS: ["ifInUcastPkts", "ifInUcastPkts_rate", "ifOutUcastPkts", "ifOutUcastPkts_rate", "ifInErrors",
            "ifInErrors_rate", "ifOutErrors", "ifOutErrors_rate", "ifOctets_rate", "ifUcastPkts_rate",
            "ifErrors_rate", "ifInOctets", "ifInOctets_rate", "ifOutOctets", "ifOutOctets_rate", "ifInOctets_perc",
            "ifOutOctets_perc", "ifInErrors", "ifOutErrors", "ifInNUcastPkts", "ifInNUcastPkts_rate",
            "ifOutNUcastPkts", "ifOutNUcastPkts_rate", "ifInBroadcastPkts", "ifInBroadcastPkts_rate",
            "ifOutBroadcastPkts", "ifOutBroadcastPkts_rate", "ifInMulticastPkts", "ifInMulticastPkts_rate",
            "ifOutMulticastPkts", "ifOutMulticastPkts_rate", "port_mcbc", "ifInDiscards", "ifInDiscards_rate",
            "ifOutDiscards", "ifOutDiscards_rate", "ifDiscards_rate"],
    MEMPOOLS: ["mempool_perc", "mempool_used", "mempool_free", "mempool_total"],
    PROCESSORS: ["processor_usage"],
    STORAGE: ["storage_free", "storage_used", "storage_perc"],
}

DEFAULT_DIMENSIONS = {
    PORTS: ["ifName", "ifAlias", "ifDescr", "ifSpeed", "sysName", "location", "processor_type", "processor_name",
            "Memory_Pool_ID", "Memory_Pool_Description", "Memory_Pool_Vendor", "storage_description", "storage_type"],
    MEMPOOLS: ["mempool_id", "mempool_descr", "mempool_mib"],
    PROCESSORS: ["processor_type", "processor_descr"],
    STORAGE: ["storage_descr", "storage_type"],
}


class ObserviumScript(Source):
    JYTHON_SCRIPT = 'observium.py'

    def endpoint(self) -> str:
        return self.pipeline.source.config['endpoint']

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
                {'key': 'URL', 'value': self.pipeline.source.config['url']},
                {'key': 'API_USER', 'value': self.pipeline.source.config[source.ObserviumSource.USERNAME]},
                {'key': 'API_PASSWORD', 'value': self.pipeline.source.config[source.ObserviumSource.PASSWORD]},
                {'key': 'PARAMS', 'value': self._params()},
                {'key': 'MEASUREMENTS', 'value': self._measurements()},
                {'key': 'DIMENSIONS', 'value': self._dimensions()},
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

    def _params(self) -> dict:
        params = self.pipeline.source.config.get('params')
        if params:
            return {k: v for k, v in params.items() if v and (k in ALLOWED_PARAMS[self.endpoint()])}
        return {}

    def _measurements(self) -> dict:
        if self.pipeline.values:
            return self.pipeline.values
        return DEFAULT_MEASUREMENTS[self.endpoint()]

    def _dimensions(self) -> list:
        if self.pipeline.dimensions:
            return self.pipeline.dimensions
        return DEFAULT_DIMENSIONS[self.endpoint()]
