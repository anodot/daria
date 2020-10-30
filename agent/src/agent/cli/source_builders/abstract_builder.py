from abc import ABC, abstractmethod
from agent import source, pipeline, streamsets
from agent.modules import tools
from agent.modules.logger import get_logger

logger = get_logger(__name__)


class Builder(ABC):
    def __init__(self, source_: source.Source):
        self.source = source_
        self.validator = source.validator.get_validator(self.source)

    @abstractmethod
    def prompt(self, default_config, advanced=False) -> source.Source:
        pass

    @staticmethod
    def _get_preview_data(test_pipeline: pipeline.Pipeline):
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

    def _get_sample_records(self, pipeline_: pipeline.Pipeline):
        preview_data, errors = self._get_preview_data(pipeline_)

        if not preview_data:
            print('No preview data available')
            return

        try:
            data = preview_data['batchesOutput'][0][0]['output']['source_outputLane']
        except (ValueError, TypeError, IndexError) as e:
            logger.exception(str(e))
            print('No preview data available')
            return [], []
        return [tools.sdc_record_map_to_dict(record['value']) for record in data[:source.manager.MAX_SAMPLE_RECORDS]], errors

    @tools.if_validation_enabled
    def print_sample_data(self, pipeline_: pipeline.Pipeline):
        records, errors = self._get_sample_records(pipeline_)
        if records:
            tools.print_dicts(records)
        print(*errors, sep='\n')
