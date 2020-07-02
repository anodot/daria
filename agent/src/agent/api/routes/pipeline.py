from jsonschema import ValidationError

from agent.api.routes import needs_pipeline
from agent.pipeline import manager
from flask import jsonify, Blueprint, request
from agent.api import routes
from agent.pipeline.pipeline import PipelineException
from agent.repository import pipeline_repository
from agent import source
from agent.streamsets_api_client import api_client, StreamSetsApiClientException

pipelines = Blueprint('pipelines', __name__)


@pipelines.route('/pipelines', methods=['GET'])
def list_pipelines():
    configs = []
    for p in pipeline_repository.get_all():
        configs.append(p.to_dict())
    return jsonify(configs)


@pipelines.route('/pipelines', methods=['POST'])
@routes.needs_destination
def create():
    json = request.get_json()
    try:
        manager.validate_json_for_create(json)
        source_instances = []
        for config in json:
            source_instances.append(manager.create_from_json(config).to_dict())
    except (ValidationError, PipelineException, source.SourceNotExists, source.SourceConfigDeprecated) as e:
        return jsonify(str(e)), 400
    return jsonify(source_instances)


@pipelines.route('/pipelines', methods=['PUT'])
def edit():
    try:
        pipeline_instances = []
        for config in request.get_json():
            pipeline_instances.append(manager.edit_using_json(config).to_dict())
    except Exception as e:
        return jsonify(str(e)), 400
    return jsonify(pipeline_instances)


@pipelines.route('/pipelines/<pipeline_id>', methods=['DELETE'])
@needs_pipeline
def delete(pipeline_id):
    manager.delete_by_id(pipeline_id)
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_id>/start', methods=['POST'])
@needs_pipeline
def start(pipeline_id):
    try:
        manager.start(pipeline_repository.get(pipeline_id))
    except (manager.PipelineFreezeException, PipelineException) as e:
        return jsonify(str(e)), 400
    return jsonify(f'Pipeline {pipeline_id} is running')


@pipelines.route('/pipelines/<pipeline_id>/stop', methods=['POST'])
@needs_pipeline
def stop(pipeline_id):
    try:
        manager.stop_by_id(pipeline_id)
    except manager.PipelineFreezeException as e:
        return jsonify(str(e)), 400


@pipelines.route('/pipelines/<pipeline_id>/force-stop', methods=['POST'])
@needs_pipeline
def force_stop(pipeline_id):
    try:
        manager.force_stop_pipeline(pipeline_id)
    except manager.PipelineFreezeException as e:
        return jsonify(str(e)), 400


@pipelines.route('/pipelines/<pipeline_id>/info')
def info(pipeline_id):
    pipeline = api_client.get_pipeline(pipeline_id)
    pipelines_status = api_client.get_pipeline_status(pipeline_id)
    return 'something'


@pipelines.route('/pipelines/<pipeline_id>/logs/<level>', methods=['GET'])
@needs_pipeline
def logs(pipeline_id, level):
    try:
        res = api_client.get_pipeline_logs(pipeline_id, level=level)
    except StreamSetsApiClientException as e:
        return jsonify(str(e)), 500
    # todo jsonify? что если там не json?
    return res.get_json()


@pipelines.route('/pipelines/<pipeline_id>/enable-destination-logs', methods=['POST'])
@needs_pipeline
def enable_destination_logs(pipeline_id):
    manager.enable_destination_logs(pipeline_repository.get(pipeline_id))
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_id>/disable-destination-logs', methods=['POST'])
@needs_pipeline
def disable_destination_logs(pipeline_id):
    manager.disable_destination_logs(pipeline_repository.get(pipeline_id))
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_id>/reset', methods=['POST'])
@needs_pipeline
def reset(pipeline_id):
    try:
        manager.reset(pipeline_repository.get(pipeline_id))
    except StreamSetsApiClientException as e:
        return jsonify(str(e)), 500
    return jsonify('logs')
