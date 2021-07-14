from agent.pipeline.config.stages.base import Stage


class DimensionsRenamer(Stage):
    def _get_config(self) -> dict:
        renameMapping = []
        for field, alias in self.pipeline.config.get('rename_dimensions_mapping', {}).items():
            renameMapping.append({
                "fromFieldExpression": f"/properties/{field}",
                "toFieldExpression": f"/properties/{alias}",
            })
        return {'renameMapping': renameMapping}
