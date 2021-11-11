from agent import source, pipeline
from agent.modules import tools
from agent.pipeline import Pipeline


def print_sample_data(pipeline_: Pipeline):
    _get_preview_type(pipeline_.source.type).print_sample_data(pipeline_)


def show_preview(pipeline_: Pipeline):
    preview_data, errors = pipeline.manager.get_preview_data(pipeline_)

    if preview_data and preview_data['batchesOutput']:
        for output in preview_data['batchesOutput'][0]:
            if 'destination_OutputLane' in output['output']:
                data = output['output']['destination_OutputLane'][:pipeline.manager.MAX_SAMPLE_RECORDS]
                if data:
                    tools.print_json([tools.sdc_record_map_to_dict(record['value']) for record in data])
                else:
                    print('Could not fetch any data matching the provided config')
                break
    else:
        print('Could not fetch any data matching the provided config')
    print(*errors, sep='\n')


class Preview:
    def print_sample_data(self, pipeline_: Pipeline):
        records, errors = pipeline.manager.get_sample_records(pipeline_)
        if not records and not errors:
            print('No preview data available')
        else:
            if records:
                self._print_sample_data(records, errors)
            print(*errors, sep='\n')

    @staticmethod
    def _print_sample_data(records, errors):
        tools.print_dicts(records)


class ElasticPreview(Preview):
    @staticmethod
    def _print_sample_data(records, errors):
        tools.print_json(records)


class InfluxPreview(Preview):
    @staticmethod
    def _print_sample_data(records, errors):
        if 'series' in records[0]['results'][0]:
            series = records[0]['results'][0]['series'][0]
            tools.print_dicts(tools.map_keys(series['values'], series['columns']))
        else:
            print('No preview data available')


class SchemalessPreview(Preview):
    def print_sample_data(self, pipeline_: Pipeline):
        records, errors = pipeline.manager.get_sample_records(pipeline_)
        if records:
            if pipeline_.source.config.get(
                    source.SchemalessSource.CONFIG_DATA_FORMAT) == source.SchemalessSource.DATA_FORMAT_CSV:
                if pipeline_.source.config.get(
                        source.SchemalessSource.CONFIG_CSV_HEADER_LINE) == source.SchemalessSource.CONFIG_CSV_HEADER_LINE_NO_HEADER:
                    # todo csv mapping is used for preview, don't forget about it
                    pipeline_.source.sample_data = \
                        tools.map_keys(records, pipeline_.source.config.get(source.SchemalessSource.CONFIG_CSV_MAPPING, {}))
                else:
                    pipeline_.source.sample_data = records
                tools.print_dicts(pipeline_.source.sample_data)
            else:
                pipeline_.source.sample_data = records
                tools.print_json(records)
        print(*errors, sep='\n')


def _get_preview_type(source_type: str) -> Preview:
    types = {
        source.TYPE_INFLUX: InfluxPreview,
        source.TYPE_KAFKA: SchemalessPreview,
        source.TYPE_MONGO: Preview,
        source.TYPE_MYSQL: Preview,
        source.TYPE_POSTGRES: Preview,
        source.TYPE_CLICKHOUSE: Preview,
        source.TYPE_ELASTIC: ElasticPreview,
        source.TYPE_SPLUNK: SchemalessPreview,
        source.TYPE_DIRECTORY: SchemalessPreview,
        source.TYPE_SAGE: Preview,
        source.TYPE_VICTORIA: Preview,
        source.TYPE_ZABBIX: SchemalessPreview,
    }
    if source_type not in source.types:
        raise ValueError(f'`{source_type}` source type isn\'t supported')
    return types[source_type]()
