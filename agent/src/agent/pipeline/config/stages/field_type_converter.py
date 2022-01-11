from agent.pipeline.config.stages.base import Stage


class FieldTypeConverter(Stage):
    def _get_converter_settings(self, fields, target_type):
        return {
            'fields': fields,
            'targetType': target_type,
            'treatInputFieldAsDate': False,
            'dataLocale': 'en,US',
            'scale': -1,
            'decimalScaleRoundingStrategy': 'ROUND_UNNECESSARY',
            'dateFormat': 'YYYY_MM_DD',
            'zonedDateTimeFormat': 'ISO_ZONED_DATE_TIME',
            'encoding': 'UTF-8'
        }

    def get_config(self) -> dict:
        measurements = [f'/measurements/{measurement_name}' for measurement_name in self.pipeline.measurement_names]

        return {
            'fieldTypeConverterConfigs': [
                self._get_converter_settings(measurements, 'DECIMAL'),
                self._get_converter_settings(['/timestamp'], 'INTEGER'),
            ],
        }
