from agent.pipeline.config.stages.base import Stage


class DimensionsRenamer(Stage):
    DIMENSIONS_PATH = '/properties/'

    def get_config(self) -> dict:
        renameMapping = []
        for field, alias in self.pipeline.config.get('rename_dimensions_mapping', {}).items():
            renameMapping.append({
                "fromFieldExpression": f"{self.DIMENSIONS_PATH}{field}",
                "toFieldExpression": f"{self.DIMENSIONS_PATH}{alias}",
            })
        return {'renameMapping': renameMapping}


class SchemaDimensionsRenamer(DimensionsRenamer):
    DIMENSIONS_PATH = '/dimensions/'
