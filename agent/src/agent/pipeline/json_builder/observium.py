from typing import Optional
from agent import source
from agent.modules import field
from agent.pipeline.json_builder import Builder

HOST_NAME = 'Host Name'
LOCATION = 'Location'

POLL_TIME_KEYS = {
    'ports': 'poll_time',
    'mempools': 'mempool_polled',
    'processors': 'processor_polled',
    'storage': 'storage_polled',
}


class ObserviumBuilder(Builder):
    VALIDATION_SCHEMA_FILE_NAME = 'observium'

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
            "ifDiscards_rate": "counter",
        },
        source.ObserviumSource.MEMPOOLS: {
            "mempool_perc": "gauge",
            "mempool_used": "counter",
            "mempool_free": "counter",
            "mempool_total": "counter",
        },
        source.ObserviumSource.PROCESSORS: {
            "processor_usage": "gauge",
        },
        source.ObserviumSource.STORAGE: {
            "storage_free": "counter",
            "storage_used": "counter",
            "storage_perc": "gauge",
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
        },
        source.ObserviumSource.STORAGE: {
            'storage_description': {
                'value_path': 'storage_descr'
            },
        },
    }

    def _load_config(self):
        super()._load_config()
        self.config['uses_schema'] = True
        # _dimensions() should be after _dimension_configurations()
        self.config['dimension_configurations'] = self._dimension_configurations()
        self.config['dimensions'] = self._dimensions()
        self._validate_dimensions()
        self.config['values'] = self._measurements()
        self.config['timestamp'] = self._timestamp()
        return self.config

    def default_values_type(self) -> Optional[str]:
        return self.config.get('default_values_type')

    def _measurements(self) -> dict:
        if self.config.get('values') or not self.default_values_type():
            return self.config.get('values')
        return self.DEFAULT_MEASUREMENTS[self.default_values_type()]

    def _dimensions(self) -> list:
        if self.config.get('dimensions') or not self.default_values_type():
            dims = self.config.get('dimensions', [])
        else:
            dims = self.DEFAULT_DIMENSIONS[self.default_values_type()]
        # all observium pipelines by default have these dimensions
        # they are added from `devices` and `devices_locations` tables
        if HOST_NAME not in dims:
            dims.append(HOST_NAME)
        if LOCATION not in dims:
            dims.append(LOCATION)
        return dims

    def _dimension_configurations(self):
        if self.config.get('dimensions') or not self.default_values_type():
            dim_configurations = self.config.get('dimension_configurations', {})
        else:
            # if there are no dimensions we'll use the default ones so need to use default configs as well
            dim_configurations = self.DEFAULT_DIMENSION_CONFIGURATIONS[self.default_values_type()]
        if HOST_NAME not in dim_configurations:
            dim_configurations[HOST_NAME] = {field.Variable.VALUE_PATH: 'sysName'}
        if LOCATION not in dim_configurations:
            dim_configurations[LOCATION] = {field.Variable.VALUE_PATH: 'location'}
        return dim_configurations

    def _validate_dimensions(self):
        for dim_name in self.config['dimension_configurations'].keys():
            if dim_name not in self.config['dimensions']:
                raise Exception(f'`{dim_name}` from dimension_configurations is not specified in dimensions')

    def _timestamp(self) -> dict:
        if 'timestamp' in self.config:
            timestamp_type = self.config['timestamp']['type']
            if timestamp_type != 'unix':
                raise Exception(
                    f"Timestamp type {timestamp_type} is not supported, currently only `unix` type is supported"
                )
            return self.config['timestamp']
        elif self.default_values_type():
            return {'name': POLL_TIME_KEYS[self.default_values_type()], 'type': 'unix'}
        else:
            raise Exception('Neither `timestamp` nor `default_values_type` are specified')
