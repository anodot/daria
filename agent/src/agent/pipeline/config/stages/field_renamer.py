from agent.pipeline.config.stages.base import Stage


class DimensionsRenamer(Stage):
    DIMENSIONS_PATH = '/properties/'

    def get_config(self) -> dict:
        return self._get_config(self.pipeline.config.get('rename_dimensions_mapping', {}))

    def _get_config(self, rename_mapping: dict):
        renameMapping = [{
                'fromFieldExpression': f'{self.DIMENSIONS_PATH}{field}',
                'toFieldExpression': f'{self.DIMENSIONS_PATH}{alias}',
            } for field, alias in rename_mapping.items()]
        return {'renameMapping': renameMapping}


class SchemaDimensionsRenamer(DimensionsRenamer):
    DIMENSIONS_PATH = '/dimensions/'
