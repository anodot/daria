# https://json-schema.org/latest/json-schema-validation.html#rfc.section.6.5.3
# https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html
config_schema = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'pipeline_id': {'type': 'string'},  # name of the pipeline
            'source': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'enum': ['mongo']},
                    'config': {'type': 'object', 'properties': {
                        'configBean.mongoConfig.connectionString': {'type': 'string'},
                        'configBean.mongoConfig.username': {'type': 'string'},
                        'configBean.mongoConfig.password': {'type': 'string'},
                        'configBean.mongoConfig.database': {'type': 'string'},
                        'configBean.mongoConfig.collection': {'type': 'string'},
                        'configBean.isCapped': {'type': 'boolean'},
                        'configBean.initialOffset': {'type': 'string'},  # date
                    }},
                },
                'required': ['name', 'config']
            },
            'measurement_name': {'type': 'string'},
            'value': {
                'type': 'object',
                'properties': {
                    'type': {'type': 'string', 'enum': ['column', 'constant']},
                    'value': {'type': 'string'}
                },
                'required': ['type', 'value']
            },
            'target_type': {'type': 'string', 'enum': ['counter', 'gauge']},  # default gauge
            'timestamp': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'type': {'type': 'string', 'enum': ['string', 'datetime', 'unix', 'unix_ms']},
                    'format': {'type': 'string'}  # if string specify date format
                },
                'required': ['name', 'type'],
            },
            'dimensions': {
                'type': 'object',
                'properties': {
                    'required': {'type': 'array', 'items': {'type': 'string'}},
                    'optional': {'type': 'array', 'items': {'type': 'string'}}
                },
                'required': ['required']},
            'destination': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'enum': ['http']},
                    'config': {'type': 'object', 'properties': {
                        'conf.resourceUrl': {'type': 'string'},  # anodot metric api url with token and protocol params
                    }},
                },
                'required': ['name', 'config']
            },
        },
        'required': ['pipeline_id', 'source', 'measurement_name', 'value',
                     'dimensions', 'timestamp', 'destination']},
}