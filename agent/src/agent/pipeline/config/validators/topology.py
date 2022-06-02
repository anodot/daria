import json
import os
import jsonschema

from agent.data_extractor import topology
from agent.pipeline import Pipeline
from agent.pipeline.config.validators import Validator, validators


class TopologyValidator(Validator):
    def validate(self, pipeline_: Pipeline):
        errors = []
        for entity_type, entity in pipeline_.config['entity'].items():
            if entity_type.upper() not in topology.ENTITIES:
                errors.append(f'Invalid entity type: {entity_type}')
                continue
            with open(self._get_validation_file_path(entity_type)) as schema_file:
                json_schema = json.load(schema_file)
                try:
                    jsonschema.validate(entity, json_schema)
                except jsonschema.ValidationError as e:
                    errors.append(f'Invalid entity config for {entity_type}: {e}')
        if errors:
            raise validators.ValidationException('\n'.join(errors))

    # todo duplicate
    def _get_validation_file_path(self, entity_type):
        return os.path.join(self.definitions_dir, f'{entity_type}.json')

    @property
    def definitions_dir(self):
        return os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '../../json_builder/json_schema_definitions/topology_entities'
        )
