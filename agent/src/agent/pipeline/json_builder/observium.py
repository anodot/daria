from agent import source
from agent.pipeline.json_builder import Builder


class ObserviumBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'observium'

    ALLOWED_PARAMS = {
        source.ObserviumSource.PORTS: [
            "location", "device_id", "group", "disable", "deleted", "ignore", "ifSpeed", "ifType", "hostname",
            "ifAlias", "ifDescr", "port_descr_type", "errors", "alerted", "state", "cbqos", "mac_accounting"
        ],
        source.ObserviumSource.MEMPOOLS: ["group_id", "device_id", "mempool_descr"],
        source.ObserviumSource.PROCESSORS: ["group_id", "device_id", "processor_descr"],
        source.ObserviumSource.STORAGE: ["group_id", "device_id", "storage_descr"],
    }

    DEFAULT_MEASUREMENTS = {
        source.ObserviumSource.PORTS: {
            "ifInUcastPkts": "counter",
            "ifInUcastPkts_rate": "counter",
            "ifOutUcastPkts": "counter",
            "ifOutUcastPkts_rate": "counter",
            "ifInErrors": "counter",
            "ifInErrors_rate": "counter",
            "ifOutErrors": "counter",
            "ifOutErrors_rate": "counter",
            "ifOctets_rate": "counter",
            "ifUcastPkts_rate": "counter",
            "ifErrors_rate": "counter",
            "ifInOctets": "counter",
            "ifInOctets_rate": "counter",
            "ifOutOctets": "counter",
            "ifOutOctets_rate": "counter",
            "ifInOctets_perc": "gauge",
            "ifOutOctets_perc": "gauge",
            "ifInNUcastPkts": "counter",
            "ifInNUcastPkts_rate": "counter",
            "ifOutNUcastPkts": "counter",
            "ifOutNUcastPkts_rate": "counter",
            "ifInBroadcastPkts": "counter",
            "ifInBroadcastPkts_rate": "counter",
            "ifOutBroadcastPkts": "counter",
            "ifOutBroadcastPkts_rate": "counter",
            "ifInMulticastPkts": "counter",
            "ifInMulticastPkts_rate": "counter",
            "ifOutMulticastPkts": "counter",
            "ifOutMulticastPkts_rate": "counter",
            "port_mcbc": "counter",
            "ifInDiscards": "counter",
            "ifInDiscards_rate": "counter",
            "ifOutDiscards": "counter",
            "ifOutDiscards_rate": "counter",
            "ifDiscards_rate": "counter"
        },
        source.ObserviumSource.MEMPOOLS: {
            "mempool_perc": "gauge", "mempool_used": "counter", "mempool_free": "counter", "mempool_total": "counter"
        },
        source.ObserviumSource.PROCESSORS: {"processor_usage": "gauge"},
        source.ObserviumSource.STORAGE: {"storage_free": "counter", "storage_used": "counter", "storage_perc": "gauge"},
    }

    DEFAULT_DIMENSIONS = {
        # todo add Host_Name and Location somewhere in one place
        source.ObserviumSource.PORTS: ['Interface_Name', 'Interface_Alias', 'Interface_Description', 'Bandwidth'],
        source.ObserviumSource.MEMPOOLS: ['Memory_Pool_ID', 'Memory_Pool_Description', 'Memory_Pool_Vendor'],
        source.ObserviumSource.PROCESSORS: ["processor_type", "processor_name"],
        source.ObserviumSource.STORAGE: ["storage_description", "storage_type"],
    }

    def _load_config(self):
        super()._load_config()
        self.config['timestamp'] = {'type': 'unix'}
        self.config['uses_schema'] = True
        self.config['dimension_paths'] = self._default_dimension_paths()
        self.config['dimensions'] = self._dimensions()
        self.config['values'] = self._measurements()
        self.config['request_params'] = self._request_params()
        return self.config

    def _measurements(self) -> dict:
        return self.config.get('values') or self.DEFAULT_MEASUREMENTS[self.endpoint()]

    def _dimensions(self) -> list:
        dims = self.config.get('dimensions') or self.DEFAULT_DIMENSIONS[self.endpoint()]
        # all observium pipelines by default have these dimensions, they are added in the observium jython script
        if 'sysName' not in dims:
            dims.append('sysName')
        if 'location' not in dims:
            dims.append('location')
        return dims

    def endpoint(self) -> str:
        return self.pipeline.source.config['endpoint']

    def _request_params(self) -> dict:
        params = self.config.get('params')
        if params:
            return {k: v for k, v in params.items() if v and (k in self.ALLOWED_PARAMS[self.endpoint()])}
        return {}

    def _default_dimension_paths(self):
        if self.config.get('dimensions'):
            return self.pipeline.config.get('rename_dimensions_mapping', {})
        # if there are no dimensions we'll use the default ones so need to use default rename as well
        if self.endpoint() == source.ObserviumSource.PORTS:
            return {
                'Interface_Name': 'ifName',
                'Interface_Alias': 'ifAlias',
                'Interface_Description': 'ifDescr',
                'Bandwidth': 'ifSpeed',
                'Host_Name': 'sysName',
                'Location': 'location',
            }
        if self.endpoint() == source.ObserviumSource.MEMPOOLS:
            return {
                'Memory_Pool_ID': 'mempool_id',
                'Memory_Pool_Description': 'mempool_descr',
                'Memory_Pool_Vendor': 'mempool_mib',
                'Host_Name': 'sysName',
                'Location': 'location',
            }
        if self.endpoint() == source.ObserviumSource.PROCESSORS:
            return {
                'processor_name': 'processor_descr',
                'Host_Name': 'sysName',
                'Location': 'location',
            }
        if self.endpoint() == source.ObserviumSource.STORAGE:
            return {
                'storage_description': 'storage_descr',
                'Host_Name': 'sysName',
                'Location': 'location',
            }
