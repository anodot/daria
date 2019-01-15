import config
import time

from logger import get_logger
from pipeline_config import PipelineConfigHandler
from streamsets_api_client import StreamSetsApiClient


logger = get_logger(__name__)
config_handler = PipelineConfigHandler(config.pipeline_config)

api_client = StreamSetsApiClient(config.streamsets_username, config.streamsets_password)
pipeline = api_client.create_pipeline('test impressions')

new_config = config_handler.override_base_config(pipeline['uuid'], pipeline['title'])
api_client.update_pipeline(pipeline['pipelineId'], new_config)

pipeline_rules = api_client.get_pipeline_rules(pipeline['pipelineId'])
new_rules = config_handler.override_base_rules(pipeline_rules['uuid'])
api_client.update_pipeline_rules(pipeline['pipelineId'], new_rules)

api_client.start_pipeline(pipeline['pipelineId'])

time.sleep(13)
api_client.stop_pipeline(pipeline['pipelineId'])
