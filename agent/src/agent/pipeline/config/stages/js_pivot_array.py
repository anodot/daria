from .base import JSProcessor


class JSPivotArray(JSProcessor):
    JS_SCRIPT_NAME = 'pivot.js'

    def get_js_vars(self):
        return f"""
    state['VALUES_ARRAY_PATH'] = '{self.pipeline.values_array_path}';
        """

    def get_config(self) -> dict:
        return {'initScript': self.get_js_vars(), 'script': self._get_script()}
