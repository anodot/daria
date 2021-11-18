import requests
import urllib.parse

from flask import jsonify, Blueprint, request
from agent import monitoring as monitoring_, destination, pipeline
from agent.modules import constants, proxy
from prometheus_client import generate_latest


monitoring_bp = Blueprint('monitoring', __name__)


@monitoring_bp.route('/metrics', methods=['GET'])
def metrics():
    monitoring_.pull_latest()
    return generate_latest(registry=monitoring_.metrics.registry)


def _send_to_anodot(data: list, url: str, proxy_obj: proxy.Proxy):
    errors = []
    res = requests.post(url, json=data, proxies=proxy.get_config(proxy_obj))
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
    monitoring_url = constants.MONITORING_URL or destination_.url
    monitoring_token = constants.MONITORING_TOKEN or destination_.token

    errors = []
    if constants.MONITORING_SEND_TO_CLIENT:
        url = urllib.parse.urljoin(monitoring_url,
                                   f'api/v1/metrics?token={monitoring_token}&protocol={destination_.PROTOCOL_20}')
        errors += _send_to_anodot(data, url, destination_.proxy)

    if constants.MONITORING_SEND_TO_ANODOT:
        url = urllib.parse.urljoin(monitoring_url,
                                   f'api/v1/agents?token={monitoring_token}&protocol={destination_.PROTOCOL_20}')
        errors += _send_to_anodot(data, url, destination_.proxy)

    if errors:
        raise Exception('Errors from anodot: ' + str(errors))

    return jsonify('')


@monitoring_bp.route('/monitoring/source_http_error/<pipeline_id>/<code>', methods=['POST'])
def source_http_error(pipeline_id, code):
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    monitoring_.metrics.SOURCE_HTTP_ERRORS.labels(pipeline_.streamsets.url,
                                                  pipeline_id, pipeline_.source.type, code).inc(1)
    return jsonify('')


@monitoring_bp.route('/monitoring/scheduled_script_error/<script_name>', methods=['POST'])
def scheduled_script_error(script_name):
    monitoring_.metrics.SCHEDULED_SCRIPTS_ERRORS.labels(script_name).inc(1)
    return jsonify('')


@monitoring_bp.route('/monitoring/scheduled_script_execution_time/<script_name>', methods=['POST'])
def scheduled_script_execution_time(script_name):
    monitoring_.metrics.SCHEDULED_SCRIPT_EXECUTION_TIME.labels(script_name).set(request.json['duration'])
    return jsonify('')


@monitoring_bp.route('/monitoring/directory_file_processed/<pipeline_id>', methods=['POST'])
def directory_file_processed(pipeline_id):
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    monitoring_.metrics.DIRECTORY_FILE_PROCESSED\
        .labels(pipeline_.streamsets.url, pipeline_.name)\
        .inc(1)
    return jsonify('')


@monitoring_bp.route('/monitoring/watermark_delta/<pipeline_id>', methods=['POST'])
def watermark_delta(pipeline_id):
    delta = request.args.get('delta')
    assert delta or delta == 0
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    monitoring_.metrics.WATERMARK_DELTA\
        .labels(pipeline_.streamsets.url, pipeline_.name, pipeline_.source.type)\
        .set(delta)
    return jsonify('')
