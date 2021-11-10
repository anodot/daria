from agent.pipeline.config.stages.base import Stage


class FieldTypeConverter(Stage):
    def get_config(self) -> dict:
        config = {
            'fields': [],
            'targetType': 'DECIMAL',
            'treatInputFieldAsDate': False,
            'dataLocale': 'en,US',
            'scale': -1,
            'decimalScaleRoundingStrategy': 'ROUND_UNNECESSARY',
            'dateFormat': 'YYYY_MM_DD',
            'zonedDateTimeFormat': 'ISO_ZONED_DATE_TIME',
            'encoding': 'UTF-8'
        }
        config['fields'].append('/timestamp')
        for measurement_name in self.pipeline.measurement_names:
            config['fields'].append(f'/measurements/{measurement_name}')
        return {'fieldTypeConverterConfigs': [config]}
