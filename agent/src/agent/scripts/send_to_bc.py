import time
import traceback
import requests
from requests import HTTPError

from agent import pipeline, destination
from agent.destination.anodot_api_client import AnodotApiClient
from agent.modules.logger import get_logger

destination_ = destination.repository.get()
logger = get_logger(__name__)


def send_error_metric(pipeline_id=None):
    metric = {
        'properties': {
            'what': 'agent_to_bc_error',
        },
        'value': 1,
        'timestamp': int(time.time())
    }
    if pipeline_id:
        metric['properties']['pipeline_id'] = pipeline_id
    requests.post(destination_.resource_url, json=metric)


try:
    api_client = AnodotApiClient(destination_)
    pipelines = pipeline.repository.get_all()
except Exception:
    send_error_metric()
    raise

num_of_errors = 0
for pipeline_ in pipelines:
    if not pipeline.manager.is_monitoring(pipeline_):
        try:
            api_client.send_pipeline_data_to_bc(pipeline.manager.transform_for_bc(pipeline_))
        except HTTPError as e:
            if not e.response.status_code == 404:
                num_of_errors += 1
                send_error_metric(pipeline_.name)
                logger.error(traceback.format_exc())
        except Exception:
            num_of_errors += 1
            send_error_metric(pipeline_.name)
            logger.error(traceback.format_exc())


for deleted_pipeline_id in pipeline.repository.get_deleted_pipeline_ids():
    try:
        api_client.delete_pipeline_from_bc(deleted_pipeline_id[0])
    except HTTPError as e:
        if not e.response.status_code == 404:
            num_of_errors += 1
            send_error_metric(deleted_pipeline_id)
            logger.error(traceback.format_exc())
    except Exception:
        num_of_errors += 1
        send_error_metric(deleted_pipeline_id)
        logger.error(traceback.format_exc())
    pipeline.repository.remove_deleted_pipeline_id(deleted_pipeline_id)

exit(num_of_errors)
