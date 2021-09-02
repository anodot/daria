import traceback
import requests

from agent import pipeline, destination, monitoring
from agent.destination.anodot_api_client import AnodotApiClient
from agent.modules.logger import get_logger

destination_ = destination.repository.get()
logger = get_logger(__name__, stdout=True)


def _update_errors_count(num_of_errors: int):
    monitoring.increase_scheduled_script_error_counter('agent-to-bc')
    return num_of_errors + 1


def main():
    num_of_errors = 0
    try:
        api_client = AnodotApiClient(destination_)
        pipelines = pipeline.repository.get_all()
    except Exception:
        _update_errors_count(0)
        raise

    for pipeline_ in pipelines:
        try:
            api_client.send_pipeline_data_to_bc(pipeline.manager.transform_for_bc(pipeline_))
        except requests.HTTPError as e:
            if not e.response.status_code == 404:
                num_of_errors = _update_errors_count(num_of_errors)
                logger.error(traceback.format_exc())
        except Exception:
            num_of_errors = _update_errors_count(num_of_errors)
            logger.error(f'Error sending pipeline {pipeline_.name}')
            logger.error(traceback.format_exc())

    for deleted_pipeline_id in pipeline.repository.get_deleted_pipeline_ids():
        deleted_pipeline_id = deleted_pipeline_id[0]
        try:
            api_client.delete_pipeline_from_bc(deleted_pipeline_id)
            pipeline.repository.remove_deleted_pipeline_id(deleted_pipeline_id)
        except requests.HTTPError as e:
            if not e.response.status_code == 404:
                num_of_errors = _update_errors_count(num_of_errors)
                logger.error(traceback.format_exc())
        except Exception:
            num_of_errors = _update_errors_count(num_of_errors)
            logger.error(traceback.format_exc())
    return num_of_errors


if __name__ == '__main__':
    exit(main())
