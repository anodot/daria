import calendar
import pytz

from datetime import datetime

from flask import jsonify, Blueprint, request
from agent import monitoring, destination, pipeline
from prometheus_client import multiprocess, generate_latest

multiprocess.MultiProcessCollector(monitoring.metrics.registry)
monitoring_bp = Blueprint('monitoring', __name__)


@monitoring_bp.route('/metrics', methods=['GET'])
def metrics():
    monitoring.pull_latest()

    def to_prometheus_format(metric):
        values = ''
        for sample in metric.samples:
            values += f'\n{sample.name}'
            if sample.labels:
                values += '{' + ','.join([f'{name}="{val}"' for name, val in sample.labels.items()]) + '}'
            values += f' {sample.value}'
        return f"# HELP {metric.name} {metric.documentation}\n# TYPE {metric.name} {metric.type}{values}"
    return '\n'.join([to_prometheus_format(metric) for metric in monitoring.metrics.collect_metrics()])


@monitoring_bp.route('/monitoring', methods=['GET'])
def monitoring_():
    try:
        destination_ = destination.repository.get()
    except destination.repository.DestinationNotExists:
        return jsonify('')

    if errors := monitoring.sender.send_monitoring_data(destination_):
        raise MonitoringException(errors)

    return jsonify('')


@monitoring_bp.route('/monitoring/source_http_error/<pipeline_id>/<code>', methods=['POST'])
def source_http_error(pipeline_id, code):
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    monitoring.metrics.SOURCE_HTTP_ERRORS.labels(pipeline_id, pipeline_.source.type, code).inc(1)
    return jsonify('')


@monitoring_bp.route('/monitoring/scheduled_script_error/<script_name>', methods=['POST'])
def scheduled_script_error(script_name):
    monitoring.metrics.SCHEDULED_SCRIPTS_ERRORS.labels(script_name).inc(1)
    return jsonify('')


@monitoring_bp.route('/monitoring/scheduled_script_execution_time/<script_name>', methods=['POST'])
def scheduled_script_execution_time(script_name):
    monitoring.metrics.SCHEDULED_SCRIPT_EXECUTION_TIME.labels(script_name).set(request.json['duration'])
    return jsonify('')


@monitoring_bp.route('/monitoring/directory_file_processed/<pipeline_id>', methods=['POST'])
def directory_file_processed(pipeline_id):
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    monitoring.metrics.DIRECTORY_FILE_PROCESSED\
        .labels(pipeline_.streamsets.url, pipeline_.name)\
        .inc(1)
    return jsonify('')


@monitoring_bp.route('/monitoring/watermark_sent/<pipeline_id>', methods=['POST'])
def watermark_sent(pipeline_id):
    data = request.get_json()
    if type(data) is not dict or 'watermark' not in data:
        return jsonify({'errors': 'wrong data format'}), 400

    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    if not pipeline_:
        return jsonify({}), 404

    tz = pipeline_.timezone if pipeline_.watermark_in_local_timezone and pipeline_.timezone else 'UTC'
    delta = str(calendar.timegm(datetime.now(pytz.timezone(tz)).timetuple()) - data['watermark'])

    monitoring.metrics.WATERMARK_DELTA \
        .labels(pipeline_.streamsets.url, pipeline_.name, pipeline_.source.type) \
        .set(delta)
    monitoring.metrics.WATERMARK_SENT\
        .labels(pipeline_.streamsets.url, pipeline_.name, pipeline_.source.type)\
        .inc(1)

    return jsonify('')


class MonitoringException(Exception):
    pass
