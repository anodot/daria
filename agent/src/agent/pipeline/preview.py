from agent import streamsets, source
from agent.modules import tools
from agent.modules.tools import if_validation_enabled
from agent.pipeline import Pipeline
from agent.modules.logger import get_logger

logger = get_logger(__name__)

MAX_SAMPLE_RECORDS = 3


def _get_preview_data(test_pipeline: Pipeline):
    streamsets.manager.create(test_pipeline)
    try:
        preview = streamsets.manager.create_preview(test_pipeline)
        preview_data, errors = streamsets.manager.wait_for_preview(test_pipeline, preview['previewerId'])
    except (Exception, KeyboardInterrupt) as e:
        logger.exception(str(e))
        raise
    finally:
        streamsets.manager.delete(test_pipeline)
    return preview_data, errors


def get_sample_records(pipeline_: Pipeline):
    preview_data, errors = _get_preview_data(pipeline_)

    if not preview_data:
        # todo this is not a place for print
        print('No preview data available')
        return

    try:
        data = preview_data['batchesOutput'][0][0]['output']['source_outputLane']
    except (ValueError, TypeError, IndexError) as e:
        logger.exception(str(e))
        print('No preview data available')
        return [], []
    return [tools.sdc_record_map_to_dict(record['value']) for record in data[:MAX_SAMPLE_RECORDS]], errors


class Preview:
    @tools.if_validation_enabled
    def print_sample_data(self, pipeline_: Pipeline):
        records, errors = get_sample_records(pipeline_)
        if records:
            tools.print_dicts(records)
        print(*errors, sep='\n')


class ElasticPreview(Preview):
    @if_validation_enabled
    def print_sample_data(self, pipeline_: Pipeline):
        records, errors = get_sample_records(pipeline_)
        if records:
            tools.print_json(records)
        print(*errors, sep='\n')


class SchemalessPreview(Preview):
    @if_validation_enabled
    def print_sample_data(self, pipeline_: Pipeline):
        records, errors = get_sample_records(pipeline_)
        if records:
            if pipeline_.source.config.get(
                    source.SchemalessSource.CONFIG_DATA_FORMAT) == source.SchemalessSource.DATA_FORMAT_CSV:
                if pipeline_.source.config.get(
                        source.SchemalessSource.CONFIG_CSV_HEADER_LINE) == source.SchemalessSource.CONFIG_CSV_HEADER_LINE_NO_HEADER:
                    pipeline_.source.sample_data = \
                        tools.map_keys(records, pipeline_.source.config.get(source.SchemalessSource.CONFIG_CSV_MAPPING, {}))
                else:
                    pipeline_.source.sample_data = records
                tools.print_dicts(pipeline_.source.sample_data)
            else:
                pipeline_.source.sample_data = records
                tools.print_json(records)
        print(*errors, sep='\n')


class InfluxPreview(Preview):
    @if_validation_enabled
    def print_sample_data(self, pipeline_: Pipeline):
        records, errors = get_sample_records(pipeline_)
        if records and 'series' in records[0]['results'][0]:
            series = records[0]['results'][0]['series'][0]
            tools.print_dicts(tools.map_keys(series['values'], series['columns']))
        else:
            print('No preview data available')
        print(*errors, sep='\n')


# todo di?
def _get_preview_type(source_type: str) -> Preview:
    types = {
        source.TYPE_INFLUX: InfluxPreview,
        source.TYPE_KAFKA: SchemalessPreview,
        source.TYPE_MONGO: Preview,
        source.TYPE_MYSQL: Preview,
        source.TYPE_POSTGRES: Preview,
        source.TYPE_ELASTIC: ElasticPreview,
        source.TYPE_SPLUNK: SchemalessPreview,
        source.TYPE_DIRECTORY: SchemalessPreview,
        source.TYPE_SAGE: Preview,
        source.TYPE_VICTORIA: Preview,
    }
    if source_type not in source.types:
        raise ValueError(f'`{source_type}` source type isn\'t supported')
    return types[source_type]()


# todo it's not a place for print
def print_sample_data(pipeline_: Pipeline):
    _get_preview_type(pipeline_.source.type).print_sample_data(pipeline_)
