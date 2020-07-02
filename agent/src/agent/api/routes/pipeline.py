from typing import Tuple

from agent.pipeline import manager
from flask import jsonify, Blueprint, request, Response
from agent.api import routes
from agent.pipeline.manager import PipelineFreezeException
from agent.pipeline.pipeline import PipelineException
from agent.repository import pipeline_repository
from agent.streamsets_api_client import api_client

pipelines = Blueprint('pipelines', __name__)


@pipelines.route('/pipelines', methods=['GET'])
def list_pipelines():
    configs = []
    for p in pipeline_repository.get_all():
        configs.append(p.to_dict())
    return jsonify(configs)


@pipelines.route('/pipelines/<pipeline_id>/info')
def info(pipeline_id):
    pipeline = api_client.get_pipeline(pipeline_id)
    pipelines_status = api_client.get_pipeline_status(pipeline_id)
    return 'something'


@pipelines.route('/pipelines', methods=['POST'])
@routes.needs_destination
def create() -> (Response, int):
    return routes.create(manager.validate_json_for_create, manager.create_from_json, request.get_json())


@pipelines.route('/pipelines', methods=['PUT'])
def edit() -> (Response, int):
    try:
        pipeline_instances = []
        for config in request.get_json():
            pipeline_instances.append(manager.edit_using_json(config).to_dict())
    except Exception as e:
        return jsonify(str(e)), 400
    return jsonify(pipeline_instances)


@pipelines.route('/pipelines/<pipeline_id>', methods=['DELETE'])
def delete(pipeline_id) -> (Response, int):
    if not pipeline_repository.exists(pipeline_id):
        return jsonify(f'Pipeline {pipeline_id} does not exist'), 400
    pipeline_repository.delete_by_id(pipeline_id)
    return ''


@pipelines.route('/pipelines/<pipeline_id>/start', methods=['DELETE'])
def start(pipeline_id) -> Tuple[Response, int]:
    if not pipeline_repository.exists(pipeline_id):
        return jsonify(f'Pipeline {pipeline_id} does not exist'), 400
    try:
        manager.start(pipeline_repository.get(pipeline_id))
    except (PipelineFreezeException, PipelineException) as e:
        return jsonify(str(e)), 400
    return jsonify(f'Pipeline {pipeline_id} is running')
