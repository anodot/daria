from flask import jsonify, Blueprint, request
from agent.repository import pipeline_repository
from agent import destination
from agent.streamsets_api_client import api_client

pipelines = Blueprint('pipelines', __name__)


@pipelines.route('/pipelines', methods=['GET'])
def list_pipelines():
    # look at https://github.com/anodot/daria/blob/d5f4f883fef3b3d5cd5cb94447b5a0c0d605e4fe/agent/src/agent/cli/pipeline.py#L221
    # откуда нужно брать пайплайны из файлов или стримсетс?
    pipeliness = api_client.get_pipelines()
    pipelines_status = api_client.get_pipelines_status()
    # print pipelines and statuses?
    # return jsonify(pipeline_repository.get_all())


@pipelines.route('/pipelines', methods=['POST'])
def create():
    if not destination.HttpDestination.exists():
        return 'Destination is not configured. Please create agent destination first', 400
    try:
        # source.validate_json_for_create(request.get_json())
        pipeline_instances = []
        # for config in request.get_json():
        #     source_instances.append(source.create_from_json(config).to_dict())
    except Exception as e:
        return str(e), 400
    return jsonify(pipeline_instances)


@pipelines.route('/pipelines', methods=['PUT'])
def edit():
    try:
        # source.validate_json_for_edit(request.get_json())
        pipeline_instances = []
        # for config in request.get_json():
        #     source_instances.append(source.edit_using_json(config).to_dict())
    except Exception as e:
        return str(e), 400
    return jsonify(pipeline_instances)


@pipelines.route('/pipelines/<pipeline_id>', methods=['DELETE'])
def delete(pipeline_id):
    try:
        pipeline_repository.delete_by_id(pipeline_id)
    except Exception as e:
        return str(e), 400
    return ''
