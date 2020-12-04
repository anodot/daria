from .base import Stage


class Source(Stage):
    def _get_config(self) -> dict:
        return self._get_source_config()
