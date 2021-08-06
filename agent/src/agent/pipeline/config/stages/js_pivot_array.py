from . import base


class JSPivotArray(base.Stage):
    JS_SCRIPT_NAME = 'pivot.js'

    def get_js_vars(self):
        return f"""
    state['VALUES_ARRAY_PATH'] = '{self.pipeline.values_array_path}';
        """

    def get_config(self) -> dict:
        with open(self._get_js_file_path(self.JS_SCRIPT_NAME)) as f:
            script = f.read()

        return {
            'initScript': self.get_js_vars(),
            'script': script
        }

