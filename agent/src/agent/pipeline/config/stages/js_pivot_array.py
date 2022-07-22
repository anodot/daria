from .base import JSProcessor


class JSPivotArray(JSProcessor):
    JS_SCRIPT_NAME = 'pivot.js'

    def get_js_vars(self):
        return f"""
state['VALUES_ARRAY_PATH'] = '{self.pipeline.values_array_path}';
state['SELECTED_PARTITIONS'] = sdc.createMap(false);
partitions = {self.pipeline.selected_kafka_partitions};
for (var i = 0; i < partitions.length; i++) {{
  state['SELECTED_PARTITIONS'][+partitions[i]] = true;
}}
        """

    def get_config(self) -> dict:
        return {'initScript': self.get_js_vars(), 'script': self._get_script()}
