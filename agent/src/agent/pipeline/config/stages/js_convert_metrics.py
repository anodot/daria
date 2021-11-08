from . import base


class JSConvertMetrics(base.Stage):
    def get_js_vars(self):
        return f"""
state['TIMESTAMP_COLUMN'] = '{self.pipeline.timestamp_path}';
state['DIMENSIONS'] = {self.pipeline.dimensions_paths};
state['DIMENSIONS_NAMES'] = {self.pipeline.dimensions_names};
state['VALUES_COLUMNS'] = {self.pipeline.values_paths};
state['MEASUREMENT_NAMES'] = {self.pipeline.measurement_names};
state['TARGET_TYPES'] = {self.pipeline.target_types_paths};
state['COUNT_RECORDS'] = {int(self.pipeline.count_records)};
state['COUNT_RECORDS_MEASUREMENT_NAME'] = '{self.pipeline.count_records_measurement_name}';
state['STATIC_WHAT'] = {int(self.pipeline.static_what)};
state['VALUES_ARRAY_PATH'] = '{self.pipeline.values_array_path}';
state['VALUES_ARRAY_FILTER'] = {self.pipeline.values_array_filter_metrics};
state['INTERVAL'] = {self.pipeline.interval if self.pipeline.interval is not None else 'null'};
state['HEADER_ATTRIBUTES'] = {self.pipeline.header_attributes};
state['metrics'] = {{}}
    """

    def get_config(self) -> dict:
        required_fields = [*self.pipeline.required_dimensions_paths, self.pipeline.timestamp_path]

        return {
            'initScript': self.get_js_vars(),
            'stageRequiredFields': [f'/{f}' for f in required_fields],
        }


class JSConvertMetrics30(JSConvertMetrics):
    JS_SCRIPT_NAME = 'protocol_3.js'

    def get_config(self) -> dict:
        with open(self._get_js_file_path(self.JS_SCRIPT_NAME)) as f:
            script = f.read()

        return {
            'initScript': self.get_js_vars(),
            'script': script,
            'stageRequiredFields': [f'/{f}' for f in [*self.pipeline.required_dimensions_paths,
                                                      self.pipeline.timestamp_path]]
        }
