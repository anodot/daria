import requests

from agent.destination import HttpDestination, anodot_api_client
from agent import monitoring
from agent.modules import constants, tools

BATCH_SIZE = 1000


def send_monitoring_data(destination_: HttpDestination) -> list:
    monitoring_api_client = anodot_api_client.MonitoringApiClient(
        constants.MONITORING_URL or destination_.url,
        constants.MONITORING_TOKEN or destination_.token,
        destination_.proxy,
        verify_ssl=not destination_.use_jks_truststore
    )

    errors = []
    for chunk in tools.chunks(monitoring.get_monitoring_metrics_for_anodot(), BATCH_SIZE):
        if constants.MONITORING_SEND_TO_CLIENT:
            try:
                monitoring_api_client.send_to_client(chunk)
            except requests.HTTPError as e:
                errors.append(f'{e.response.url} - {e.response.text}')

        if constants.MONITORING_SEND_TO_ANODOT:
            try:
                monitoring_api_client.send_to_anodot(chunk)
            except requests.HTTPError as e:
                errors.append(f'{e.response.url} - {e.response.text}')

    return errors
