from . import base


class JSConvertMetrics(base.Stage):
    def get_js_vars(self):
        return f"""
state['TIMESTAMP_COLUMN'] = '{self.pipeline.timestamp_path}';
state['DIMENSIONS'] = {self.pipeline.dimensions_paths};
state['DIMENSIONS_NAMES'] = {self.pipeline.dimensions_names};
state['VALUES_COLUMNS'] = {self.pipeline.values_paths};
state['MEASUREMENT_NAMES'] = {self.pipeline.measurement_names_paths};
state['TARGET_TYPES'] = {self.pipeline.target_types_paths};
state['COUNT_RECORDS'] = {int(self.pipeline.count_records)};
state['COUNT_RECORDS_MEASUREMENT_NAME'] = '{self.pipeline.count_records_measurement_name}';
state['STATIC_WHAT'] = {int(self.pipeline.static_what)};
state['VALUES_ARRAY_PATH'] = '{self.pipeline.values_array_path}';
state['VALUES_ARRAY_FILTER'] = {self.pipeline.values_array_filter_metrics};
state['metrics'] = {{}}
    """

    def _get_config(self) -> dict:
        return {
            'initScript': self.get_js_vars()
        }


class JSConvertMetrics30(JSConvertMetrics):
    JS_SCRIPT_NAME = 'protocol_3.js'

    def _get_config(self) -> dict:
        with open(self._get_js_file_path(self.JS_SCRIPT_NAME)) as f:
            script = f.read()

        return {
            'initScript': self.get_js_vars(),
            'script': script
        }

