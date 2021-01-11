import requests
import urllib.parse

from flask import jsonify, Blueprint
from agent import monitoring as monitoring_, destination
from agent.modules import constants


monitoring_bp = Blueprint('monitoring', __name__)


@monitoring_bp.route('/metrics', methods=['GET'])
def metrics():
    return monitoring_.get_latest()


def _send_to_anodot(data, url):
    errors = []
    res = requests.post(url, json=data)
    if res.status_code != 200:
        errors.append(f'Error {res.status_code} from {url}')

    if res.text:
        res_json = res.json()
        if res_json['errors']:
            errors.append(str(res_json['errors']))

    return errors


@monitoring_bp.route('/monitoring', methods=['GET'])
def monitoring():
    try:
        destination_ = destination.repository.get()
    except destination.repository.DestinationNotExists:
        return jsonify('')

    data = monitoring_.latest_to_anodot()
    monitoring_url = constants.MONITORING_URL if constants.MONITORING_URL else destination_.url

    errors = []
    if constants.MONITORING_SEND_TO_CLIENT:
        # add proxy
        url = urllib.parse.urljoin(monitoring_url,
                                   f'api/v1/metrics?token={destination_.token}&protocol={destination_.PROTOCOL_20}')
        errors += _send_to_anodot(data, url)

    if constants.MONITORING_SEND_TO_ANODOT:
        # add proxy
        url = urllib.parse.urljoin(monitoring_url,
                                   f'api/v1/agents?token={destination_.token}&protocol={destination_.PROTOCOL_20}')
        errors += _send_to_anodot(data, url)

    if errors:
        raise Exception('Errors from anodot: ' + str(errors))

    return jsonify('')