from .base import Stage


class Pivoter(Stage):
    def get_config(self) -> dict:
        list_path = '/'
        for value in self.pipeline.values_paths:
            if value.find('[]') >= 0:
                list_path += value.split('[]')[0]
        return {'listPath': list_path}
