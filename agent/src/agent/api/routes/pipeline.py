import logging
import time
import requests
from jsonschema import ValidationError

from agent.api.routes import needs_pipeline
from flask import jsonify, Blueprint, request
from agent.api import routes
from agent import pipeline, source
from agent.modules import proxy, logger
from agent.modules.streamsets_api_client import StreamSetsApiClientException

pipelines = Blueprint('pipelines', __name__)
logger = logger.get_logger(__name__)


@pipelines.route('/pipelines', methods=['GET'])
def list_pipelines():
    configs = []
    for p in pipeline.repository.get_all():
        configs.append(p.to_dict())
    return jsonify(configs)


@pipelines.route('/pipelines/exists/<pipeline_name>', methods=['GET'])
@routes.needs_destination
def exists(pipeline_name):
    return "yes" if pipeline.repository.exists(pipeline_name) else "no"


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
    except ValueError as e:
        return jsonify(str(e)), 400
    except pipeline.PipelineException as e:
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
        pipeline.manager.start(pipeline.repository.get_by_name(pipeline_name))
    except (pipeline.manager.PipelineFreezeException, pipeline.PipelineException) as e:
        return jsonify(str(e)), 400
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_name>/stop', methods=['POST'])
@needs_pipeline
def stop(pipeline_name):
    if not pipeline.manager.can_stop(pipeline_name):
        return f'Cannot stop the pipeline `{pipeline_name}` that is in status {pipeline.manager.get_pipeline_status(pipeline_name)}', 400
    try:
        pipeline.manager.stop_by_id(pipeline_name)
    except StreamSetsApiClientException as e:
        return jsonify(str(e)), 400
    except pipeline.manager.PipelineFreezeException as e:
        return jsonify(str(e)), 400
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_name>/force-stop', methods=['POST'])
@needs_pipeline
def force_stop(pipeline_name):
    try:
        pipeline.manager.force_stop_pipeline(pipeline_name)
    except pipeline.manager.PipelineFreezeException as e:
        return jsonify(str(e)), 400


@pipelines.route('/pipelines/<pipeline_name>/info', methods=['GET'])
@needs_pipeline
def info(pipeline_name):
    number_of_history_records = int(request.args.get('number_of_history_records', 10))
    try:
        return jsonify(pipeline.info.get(pipeline_name, number_of_history_records))
    except StreamSetsApiClientException as e:
        return jsonify(str(e)), 500


@pipelines.route('/pipelines/<pipeline_name>/logs', methods=['GET'])
@needs_pipeline
def logs(pipeline_name):
    if 'severity' in request.args and request.args['severity'] not in pipeline.manager.LOG_LEVELS:
        return f'{request.args["severity"]} logging level is not one of {", ".join(pipeline.manager.LOG_LEVELS)}', 400
    severity = request.args.get('severity', logging.getLevelName(logging.INFO))
    number_of_records = int(request.args.get('number_of_records', 10))
    try:
        return jsonify(pipeline.info.get_logs(pipeline_name, severity, number_of_records))
    except StreamSetsApiClientException as e:
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
    except StreamSetsApiClientException as e:
        return jsonify(str(e)), 500
    return jsonify('')


@pipelines.route('/pipeline-status-change', methods=['POST'])
def pipeline_status_change():
    data = request.get_json()
    pipeline_ = pipeline.repository.get_by_name(data['pipeline_name'])
    pipeline_.status = data['pipeline_status']
    pipeline.repository.save(pipeline_)

    if data['pipeline_status'] in pipeline_.error_statuses:
        _send_error_status_to_anodot(data, pipeline_)

    return ''


def _send_error_status_to_anodot(data, pipeline_):
    metric = [{
        "properties": {
            "what": "pipeline_error_status_count",
            "pipeline_name": data["pipeline_name"],
            "pipeline_status": data['pipeline_status'],
            "target_type": "counter",
        },
        "tags": pipeline_.meta_tags(),
        "timestamp": int(time.time()),
        "value": 1
    }]
    res = requests.post(
        pipeline_.destination.resource_url, json=metric, proxies=proxy.get_config(pipeline_.destination.proxy)
    )
    res.raise_for_status()
    data = res.json()
    if 'errors' in data and data['errors']:
        for error in data['errors']:
            logger.error(error['description'])
