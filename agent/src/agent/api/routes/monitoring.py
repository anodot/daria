import requests
import urllib.parse

from flask import jsonify, Blueprint
from agent import monitoring as monitoring_, destination
from agent.modules import constants


monitoring = Blueprint('monitoring', __name__)


@monitoring.route('/metrics', methods=['GET'])
def metrics():
    return monitoring_.get_latest()


@monitoring.route('/monitoring', methods=['GET'])
def metrics():
    destination_ = destination.repository.get()
    if not destination_:
        return jsonify('')

    data = monitoring_.latest_to_anodot()
    monitoring_url = constants.MONITORING_URL if constants.MONITORING_URL else destination_.url
    if constants.MONITORING_SEND_TO_CLIENT:
        # add proxy
        url = urllib.parse.urljoin(monitoring_url,
                                   f'api/v1/metrics?token={destination_.token}&protocol={destination_.PROTOCOL_20}')
        requests.post(url, json=data).raise_for_status()

    if constants.MONITORING_SEND_TO_ANODOT:
        # add proxy
        url = urllib.parse.urljoin(monitoring_url,
                                   f'api/v1/agents?token={destination_.token}&protocol={destination_.PROTOCOL_20}')
        requests.post(url, json=data).raise_for_status()

    return jsonify('')