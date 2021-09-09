from agent.pipeline.config.stages.base import Stage


class DimensionsRenamer(Stage):
    DIMENSIONS_PATH = '/properties/'

    def get_config(self) -> dict:
        return self._get_config(self.pipeline.config.get('rename_dimensions_mapping', {}))

    def _get_config(self, rename_mapping: dict):
        renameMapping = []
        for field, alias in rename_mapping.items():
            renameMapping.append({
                "fromFieldExpression": f"{self.DIMENSIONS_PATH}{field}",
                "toFieldExpression": f"{self.DIMENSIONS_PATH}{alias}",
            })
        return {'renameMapping': renameMapping}


class SchemaDimensionsRenamer(DimensionsRenamer):
    DIMENSIONS_PATH = '/dimensions/'


class ObserviumDimensionsRenamer(SchemaDimensionsRenamer):
    def get_config(self) -> dict:
        # if there are no dimensions we'll use the default ones so need to use default rename as well
        if not self.pipeline.dimensions:
            rename_mapping = _default_dimensions_rename_mapping()
        else:
            rename_mapping = self.pipeline.config.get('rename_dimensions_mapping', {})
        return self._get_config(rename_mapping)


def _default_dimensions_rename_mapping() -> dict:
    return {
        "ifName": "Interface Name",
        "ifAlias": "Interface Alias",
        "ifDescr": "Interface Description",
        "ifSpeed": "Bandwidth",
        "sysName": "Host Name",
        "location": "Location",
    }
