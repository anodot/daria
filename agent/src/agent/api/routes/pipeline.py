import logging

import requests
from jsonschema import ValidationError
from agent.api.routes import needs_pipeline
from flask import jsonify, Blueprint, request
from agent.api import routes
from agent import pipeline, source
from agent.streamsets_api_client import StreamSetsApiClientException

pipelines = Blueprint('pipelines', __name__)


@pipelines.route('/pipelines', methods=['GET'])
def list_pipelines():
    configs = []
    for p in pipeline.repository.get_all():
        configs.append(p.to_dict())
    return jsonify(configs)


@pipelines.route('/pipelines', methods=['POST'])
@routes.needs_destination
def create():
    try:
        pipelines_ = pipeline.manager.create_from_json(request.get_json())
    except (
        ValidationError, source.SourceNotExists, source.SourceConfigDeprecated, requests.exceptions.ConnectionError
    ) as e:
        return jsonify(str(e)), 400
    except pipeline.PipelineException as e:
        return jsonify(str(e)), 500
    return jsonify(list(map(lambda x: x.to_dict(), pipelines_)))


@pipelines.route('/pipelines', methods=['PUT'])
def edit():
    try:
        pipelines_ = pipeline.manager.edit_using_json(request.get_json())
    except (
        ValidationError, source.SourceNotExists, source.SourceConfigDeprecated,
        requests.exceptions.ConnectionError, pipeline.repository.PipelineNotExistsException
    ) as e:
        return jsonify(str(e)), 400
    except pipeline.PipelineException as e:
        return jsonify(str(e)), 500
    return jsonify(list(map(lambda x: x.to_dict(), pipelines_)))


@pipelines.route('/pipelines/<pipeline_id>', methods=['DELETE'])
@needs_pipeline
def delete(pipeline_id):
    pipeline.manager.delete_by_id(pipeline_id)
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_id>/start', methods=['POST'])
@needs_pipeline
def start(pipeline_id):
    try:
        pipeline.manager.start(pipeline.repository.get(pipeline_id))
    except (pipeline.manager.PipelineFreezeException, pipeline.PipelineException) as e:
        return jsonify(str(e)), 400
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_id>/stop', methods=['POST'])
@needs_pipeline
def stop(pipeline_id):
    if not pipeline.manager.can_stop(pipeline_id):
        return f'Cannot stop the pipeline `{pipeline_id}` that is in status {pipeline.manager.get_pipeline_status(pipeline_id)}', 400
    try:
        pipeline.manager.stop_by_id(pipeline_id)
    except StreamSetsApiClientException as e:
        return jsonify(str(e)), 400
    except pipeline.manager.PipelineFreezeException as e:
        return jsonify(str(e)), 400
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_id>/force-stop', methods=['POST'])
@needs_pipeline
def force_stop(pipeline_id):
    try:
        pipeline.manager.force_stop_pipeline(pipeline_id)
    except pipeline.manager.PipelineFreezeException as e:
        return jsonify(str(e)), 400


@pipelines.route('/pipelines/<pipeline_id>/info', methods=['GET'])
@needs_pipeline
def info(pipeline_id):
    number_of_history_records = int(request.args.get('number_of_history_records', 10))
    try:
        return jsonify(pipeline.info.get(pipeline_id, number_of_history_records))
    except StreamSetsApiClientException as e:
        return jsonify(str(e)), 500


@pipelines.route('/pipelines/<pipeline_id>/logs', methods=['GET'])
@needs_pipeline
def logs(pipeline_id):
    if 'severity' in request.args and request.args['severity'] not in pipeline.manager.LOG_LEVELS:
        return f'{request.args["severity"]} logging level is not one of {", ".join(pipeline.manager.LOG_LEVELS)}', 400
    severity = request.args.get('severity', logging.getLevelName(logging.INFO))
    number_of_records = int(request.args.get('number_of_records', 10))
    try:
        return jsonify(pipeline.info.get_logs(pipeline_id, severity, number_of_records))
    except StreamSetsApiClientException as e:
        return jsonify(str(e)), 500


@pipelines.route('/pipelines/<pipeline_id>/enable-destination-logs', methods=['POST'])
@needs_pipeline
def enable_destination_logs(pipeline_id):
    pipeline.manager.enable_destination_logs(pipeline.repository.get(pipeline_id))
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_id>/disable-destination-logs', methods=['POST'])
@needs_pipeline
def disable_destination_logs(pipeline_id):
    pipeline.manager.disable_destination_logs(pipeline.repository.get(pipeline_id))
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_id>/reset', methods=['POST'])
@needs_pipeline
def reset(pipeline_id):
    try:
        pipeline.manager.reset(pipeline.repository.get(pipeline_id))
    except StreamSetsApiClientException as e:
        return jsonify(str(e)), 500
    return jsonify('')
