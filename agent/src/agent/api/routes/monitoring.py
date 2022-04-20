from flask import jsonify, Blueprint, request
from agent import monitoring as monitoring_, destination, pipeline
from prometheus_client import generate_latest, multiprocess

multiprocess.MultiProcessCollector(monitoring_.metrics.registry)
monitoring_bp = Blueprint('monitoring', __name__)


@monitoring_bp.route('/metrics', methods=['GET'])
def metrics():
    monitoring_.pull_latest()
    return generate_latest(registry=monitoring_.metrics.registry)


@monitoring_bp.route('/monitoring', methods=['GET'])
def monitoring():
    try:
        destination_ = destination.repository.get()
    except destination.repository.DestinationNotExists:
        return jsonify('')

    if errors := monitoring_.data_sender.send_monitoring_data(destination_):
        raise MonitoringException(errors)

    return jsonify('')


@monitoring_bp.route('/monitoring/source_http_error/<pipeline_id>/<code>', methods=['POST'])
def source_http_error(pipeline_id, code):
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    monitoring_.metrics.SOURCE_HTTP_ERRORS.labels(pipeline_id, pipeline_.source.type, code).inc(1)
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


class MonitoringException(Exception):
    pass
