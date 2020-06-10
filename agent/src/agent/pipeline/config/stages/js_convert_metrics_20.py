from .base import Stage


class JSConvertMetrics20(Stage):
    def get_js_vars(self):
        return f"""
state['TIMESTAMP_COLUMN'] = '{self.pipeline.timestamp_path}';
state['DIMENSIONS'] = {self.pipeline.dimensions_paths};
state['DIMENSIONS_NAMES'] = {self.pipeline.dimensions_names};
state['VALUES_COLUMNS'] = {self.pipeline.values_paths};
state['MEASUREMENT_NAMES'] = {self.pipeline.measurement_names};
state['TARGET_TYPES'] = {self.pipeline.target_types};
state['COUNT_RECORDS'] = {self.pipeline.count_records};
state['COUNT_RECORDS_MEASUREMENT_NAME'] = '{self.pipeline.count_records_measurement_name}';
state['STATIC_WHAT'] = {self.pipeline.static_what};
state['metrics'] = {{}}
    """

    def get_config(self) -> dict:
        return {
            'initScript': self.get_js_vars()
        }
