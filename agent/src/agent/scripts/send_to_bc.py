import json
import traceback
import requests

from agent import pipeline, destination, monitoring
from agent.destination.anodot_api_client import AnodotApiClient
from agent.modules.logger import get_logger
from agent.modules import constants

if not constants.SEND_TO_BC:
    exit(0)

GENERAL_PIPELINE_ERROR_CODE = 70

logger = get_logger(__name__, stdout=True)


def _update_errors_count(num_of_errors: int):
    monitoring.increase_scheduled_script_error_counter('agent-to-bc')
    return num_of_errors + 1


def main():
    num_of_errors = 0
    try:
        api_client = AnodotApiClient(destination.repository.get())
        pipelines = pipeline.repository.get_all()
    except Exception:
        _update_errors_count(0)
        raise

    for pipeline_ in pipelines:
        try:
            pipeline_data = pipeline.manager.transform_for_bc(pipeline_)
            should_send_error_notification = pipeline.manager.should_send_retries_error_notification(pipeline_)
            should_send_no_data = pipeline.manager.should_send_no_data_error_notification(pipeline_)
            raise Exception(should_send_no_data, pipeline_.id, pipeline_.notifications.no_data_notification.notification_period)
            if should_send_error_notification:
                pipeline_data['notification'] = {
                    'code': GENERAL_PIPELINE_ERROR_CODE,
                    'description': 'pipeline error',
                }
            api_client.send_pipeline_data_to_bc(pipeline_data)
            if should_send_error_notification:
                logger.info(f'Error notification sent for pipeline {pipeline_.name}')
                # set 'notification_sent' flag to True
                pipeline_.retries.notification_sent = True
                pipeline.repository.save(pipeline_.retries)
        except requests.HTTPError as e:
            if e.response.status_code != 404:
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
            if e.response.status_code != 404:
                num_of_errors = _update_errors_count(num_of_errors)
                logger.error(traceback.format_exc())
        except Exception:
            num_of_errors = _update_errors_count(num_of_errors)
            logger.error(traceback.format_exc())
    return num_of_errors


if __name__ == '__main__':
    exit(main())
