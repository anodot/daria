import logging
import requests

from jsonschema import ValidationError
from agent.api.routes import needs_pipeline
from flask import jsonify, Blueprint, request
from agent.api import routes
from agent import pipeline, source, streamsets, monitoring
from agent.modules import logger

pipelines = Blueprint('pipelines', __name__)
logger = logger.get_logger(__name__)


@pipelines.route('/pipelines', methods=['GET'])
def list_pipelines():
    configs = []
    for p in pipeline.repository.get_all():
        configs.append(p.to_dict())
    return jsonify(configs)


@pipelines.route('/pipelines', methods=['POST'])
@routes.check_prerequisites
def create():
    try:
        pipelines_ = pipeline.manager.create_from_json(request.get_json())
    except (
            ValidationError, source.SourceNotExists, requests.exceptions.ConnectionError
    ) as e:
        return jsonify(str(e)), 400
    except (pipeline.PipelineException, streamsets.manager.StreamsetsException) as e:
        return jsonify(str(e)), 500
    return jsonify(list(map(lambda x: x.to_dict(), pipelines_)))


@pipelines.route('/pipelines', methods=['PUT'])
@routes.check_prerequisites
def edit():
    try:
        pipelines_ = pipeline.manager.edit_using_json(request.get_json())
    except ValueError as e:
        return jsonify(str(e)), 400
    except (pipeline.PipelineException, streamsets.manager.StreamsetsException) as e:
        return jsonify(str(e)), 500
    return jsonify(list(map(lambda x: x.to_dict(), pipelines_)))


@pipelines.route('/pipelines/<pipeline_name>', methods=['DELETE'])
@needs_pipeline
def delete(pipeline_name):
    pipeline.manager.delete_by_name(pipeline_name)
    return jsonify('')


@pipelines.route('/pipelines/force-delete/<pipeline_name>', methods=['DELETE'])
@needs_pipeline
def force_delete(pipeline_name):
    return jsonify(pipeline.manager.force_delete(pipeline_name))


@pipelines.route('/pipelines/<pipeline_name>/start', methods=['POST'])
@needs_pipeline
def start(pipeline_name):
    try:
        streamsets.manager.start(pipeline.repository.get_by_name(pipeline_name))
    except (streamsets.PipelineFreezeException, pipeline.PipelineException) as e:
        return jsonify(str(e)), 400
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_name>/stop', methods=['POST'])
@needs_pipeline
def stop(pipeline_name):
    try:
        streamsets.manager.stop(pipeline_name)
    except streamsets.ApiClientException as e:
        return jsonify(str(e)), 400
    except streamsets.PipelineFreezeException as e:
        return jsonify(str(e)), 400
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_name>/force-stop', methods=['POST'])
@needs_pipeline
def force_stop(pipeline_name):
    try:
        streamsets.manager.force_stop(pipeline_name)
    except streamsets.PipelineFreezeException as e:
        return jsonify(str(e)), 400
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_name>/info', methods=['GET'])
@needs_pipeline
def info(pipeline_name):
    number_of_history_records = int(request.args.get('number_of_history_records', 10))
    try:
        return jsonify(streamsets.manager.get_pipeline_info(pipeline_name, number_of_history_records))
    except streamsets.ApiClientException as e:
        return jsonify(str(e)), 500


@pipelines.route('/pipelines/<pipeline_name>/logs', methods=['GET'])
@needs_pipeline
def logs(pipeline_name):
    if 'severity' in request.args and request.args['severity'] not in pipeline.manager.LOG_LEVELS:
        return f'{request.args["severity"]} logging level is not one of {", ".join(pipeline.manager.LOG_LEVELS)}', 400
    severity = request.args.get('severity', logging.getLevelName(logging.INFO))
    number_of_records = int(request.args.get('number_of_records', 10))
    try:
        return jsonify(streamsets.manager.get_pipeline_logs(pipeline_name, severity, number_of_records))
    except streamsets.ApiClientException as e:
        return jsonify(str(e)), 500


@pipelines.route('/pipelines/<pipeline_name>/enable-destination-logs', methods=['POST'])
@needs_pipeline
def enable_destination_logs(pipeline_name):
    pipeline.manager.enable_destination_logs(pipeline.repository.get_by_name(pipeline_name))
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_name>/disable-destination-logs', methods=['POST'])
@needs_pipeline
def disable_destination_logs(pipeline_name):
    pipeline.manager.disable_destination_logs(pipeline.repository.get_by_name(pipeline_name))
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_name>/reset', methods=['POST'])
@needs_pipeline
def reset(pipeline_name):
    try:
        pipeline.manager.reset(pipeline.repository.get_by_name(pipeline_name))
    except streamsets.ApiClientException as e:
        return jsonify(str(e)), 500
    return jsonify('')


@pipelines.route('/pipeline-status-change/<pipeline_id>', methods=['POST'])
def pipeline_status_change(pipeline_id: str):
    data = request.get_json()
    pipeline_ = pipeline.repository.get_by_name(pipeline_id)
    pipeline_.status = data['pipeline_status']
    pipeline.repository.save(pipeline_)
    labels = (pipeline_.streamsets.url, pipeline_.name, pipeline_.source.type)
    monitoring.metrics.PIPELINE_STATUS.labels(*labels).state(pipeline_.status)
    return jsonify('')


@pipelines.route('/pipeline-offset/<pipeline_name>', methods=['POST'])
@needs_pipeline
def pipeline_offset_changed(pipeline_name):
    pipeline.manager.update_pipeline_offset(pipeline.repository.get_by_name(pipeline_name))
    return jsonify('')
