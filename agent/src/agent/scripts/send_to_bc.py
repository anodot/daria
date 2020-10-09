import time
import traceback
import requests

from agent import pipeline, destination
from agent.destination.anodot_api_client import AnodotApiClient
from agent.modules.logger import get_logger

destination_ = destination.repository.get()
logger = get_logger(__name__)

try:
    api_client = AnodotApiClient(destination_)
    pipelines = pipeline.repository.get_all()
except Exception:
    metric = [{
        'properties': {
            'what': 'agent_to_bc_error',
        },
        'value': 1,
        'timestamp': int(time.time())
    }]
    requests.post(destination_.resource_url, json=metric)
    raise

for pipeline_ in pipelines:
    if pipeline_.name != pipeline.MONITORING:
        try:
            api_client.send_pipeline_data_to_bc(pipeline.manager.transform_for_bc(pipeline_))
        except Exception:
            metric = [{
                'properties': {
                    'what': 'agent_to_bc_error',
                    'pipeline_id': pipeline_.name,
                },
                'value': 1,
                'timestamp': int(time.time())
            }]
            requests.post(destination_.resource_url, json=metric)
            logger.error(traceback.format_exc())
