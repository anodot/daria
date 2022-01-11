from agent import source
from agent.modules import field
from agent.pipeline.json_builder import Builder

HOST_NAME = 'Host Name'
LOCATION = 'Location'


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
            "mempool_perc": "gauge",
            "mempool_used": "counter",
            "mempool_free": "counter",
            "mempool_total": "counter"
        },
        source.ObserviumSource.PROCESSORS: {
            "processor_usage": "gauge"
        },
        source.ObserviumSource.STORAGE: {
            "storage_free": "counter",
            "storage_used": "counter",
            "storage_perc": "gauge"
        },
    }

    DEFAULT_DIMENSIONS = {
        source.ObserviumSource.PORTS: ['Interface Name', 'Interface Alias', 'Interface Description', 'Bandwidth'],
        source.ObserviumSource.MEMPOOLS: ['Memory_Pool_ID', 'Memory_Pool_Description', 'Memory_Pool_Vendor'],
        source.ObserviumSource.PROCESSORS: ["processor_type", "processor_name"],
        source.ObserviumSource.STORAGE: ["storage_description", "storage_type"],
    }

    DEFAULT_DIMENSION_CONFIGURATIONS = {
        source.ObserviumSource.PORTS: {
            'Interface Name': {
                'value_path': 'ifName'
            },
            'Interface Alias': {
                'value_path': 'ifAlias'
            },
            'Interface Description': {
                'value_path': 'ifDescr'
            },
            'Bandwidth': {
                'value_path': 'ifSpeed'
            },
        },
        source.ObserviumSource.MEMPOOLS: {
            'Memory_Pool_ID': {
                'value_path': 'mempool_id'
            },
            'Memory_Pool_Description': {
                'value_path': 'mempool_descr'
            },
            'Memory_Pool_Vendor': {
                'value_path': 'mempool_mib'
            },
        },
        source.ObserviumSource.PROCESSORS: {
            'processor_name': {
                'value_path': 'processor_descr'
            },
            'processor_type': {
                'value_path': 'processor_type'
            },
        },
        source.ObserviumSource.STORAGE: {
            'storage_description': {
                'value_path': 'storage_descr'
            },
        },
    }

    def _load_config(self):
        super()._load_config()
        self.config['timestamp'] = {'type': 'unix'}
        self.config['uses_schema'] = True
        self.config['dimension_configurations'] = self._dimensions_configuration()
        self.config['dimensions'] = self._dimensions()
        self.config['values'] = self._measurements()
        self.config['request_params'] = self._request_params()
        return self.config

    def _measurements(self) -> dict:
        return self.config.get('values') or self.DEFAULT_MEASUREMENTS[self.endpoint()]

    def _dimensions(self) -> list:
        dims = self.config.get('dimensions') or self.DEFAULT_DIMENSIONS[self.endpoint()]
        # all observium pipelines by default have these dimensions
        # they are added in the observium jython script from the `devices` endpoint
        if HOST_NAME not in dims:
            dims.append(HOST_NAME)
        if LOCATION not in dims:
            dims.append(LOCATION)
        return dims

    def endpoint(self) -> str:
        return self.pipeline.source.config['endpoint']

    def _request_params(self) -> dict:
        params = self.config.get('request_params')
        if params:
            return {k: v for k, v in params.items() if v and (k in self.ALLOWED_PARAMS[self.endpoint()])}
        return {}

    def _dimensions_configuration(self):
        if self.config.get('dimensions'):
            dim_configurations = self.config.get('dimension_configurations', {})
        # if there are no dimensions we'll use the default ones so need to use default configs as well
        else:
            dim_configurations = self.DEFAULT_DIMENSION_CONFIGURATIONS[self.endpoint()]
        if HOST_NAME not in dim_configurations:
            dim_configurations[HOST_NAME] = {field.Variable.VALUE_PATH: 'sysName'}
        if LOCATION not in dim_configurations:
            dim_configurations[LOCATION] = {field.Variable.VALUE_PATH: 'location'}
        return dim_configurations
