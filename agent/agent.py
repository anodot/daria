import config
import time

from logger import get_logger
from pipeline_config import PipelineConfigHandler
from streamsets_api_client import StreamSetsApiClient

time.sleep(20)
logger = get_logger(__name__)
api_client = StreamSetsApiClient(config.streamsets_username, config.streamsets_password,
                                 config.streamsets_api_base_url)

for pipeline_config in config.pipelines_config:
    config_handler = PipelineConfigHandler(pipeline_config)

    pipeline = api_client.create_pipeline(pipeline_config['name'])

    new_config = config_handler.override_base_config(pipeline['uuid'], pipeline['title'])
    api_client.update_pipeline(pipeline['pipelineId'], new_config)

    pipeline_rules = api_client.get_pipeline_rules(pipeline['pipelineId'])
    new_rules = config_handler.override_base_rules(pipeline_rules['uuid'])
    api_client.update_pipeline_rules(pipeline['pipelineId'], new_rules)

    api_client.start_pipeline(pipeline['pipelineId'])

    time.sleep(13)
    api_client.stop_pipeline(pipeline['pipelineId'])
