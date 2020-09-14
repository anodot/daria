from abc import ABC, abstractmethod
from agent import source, pipeline
from agent.modules import tools
from agent.modules.streamsets_api_client import api_client
from agent.modules.logger import get_logger


logger = get_logger(__name__)


class Builder(ABC):
    def __init__(self, source_: source.Source):
        self.source = source_
        self.validator = source.validator.get_validator(self.source)

    @abstractmethod
    def prompt(self, default_config, advanced=False) -> source.Source:
        pass

    def get_preview_data(self):
        test_pipeline_name = pipeline.manager.create_test_pipeline(self.source)
        try:
            preview = api_client.create_preview(test_pipeline_name)
            preview_data, errors = api_client.wait_for_preview(test_pipeline_name, preview['previewerId'])
        except (Exception, KeyboardInterrupt) as e:
            logger.exception(str(e))
            api_client.delete_pipeline(test_pipeline_name)
            raise
        api_client.delete_pipeline(test_pipeline_name)

        return preview_data, errors

    def get_sample_records(self):
        preview_data, errors = self.get_preview_data()

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
    def print_sample_data(self):
        records, errors = self.get_sample_records()
        if records:
            tools.print_dicts(records)
        print(*errors, sep='\n')
