from flask import jsonify, Blueprint, request
from agent import source
from agent.destination import HttpDestination
from agent.repository import source_repository

DESTINATION_DOESNT_EXIST = 'Destination is not configured. Please create agent destination first'

sources = Blueprint('test', __name__)


@sources.route('/sources', methods=['GET'])
def list_sources():
    return jsonify(source_repository.get_all())


@sources.route('/sources', methods=['POST'])
def create():
    if not HttpDestination.exists():
        return DESTINATION_DOESNT_EXIST, 400
    try:
        source.validate_json_for_create(request.get_json())
        source_instances = []
        for config in request.get_json():
            source_instances.append(source.create_from_json(config).to_dict())
    except Exception as e:
        return str(e), 400
    return jsonify(source_instances)


@sources.route('/sources', methods=['PUT'])
def edit():
    if not HttpDestination.exists():
        return DESTINATION_DOESNT_EXIST, 400
    try:
        source.validate_json_for_edit(request.get_json())
        source_instances = []
        for config in request.get_json():
            source_instances.append(source.edit_using_json(config).to_dict())
    except Exception as e:
        return str(e), 400
    return jsonify(source_instances)


@sources.route('/sources/<source_id>', methods=['DELETE'])
def delete(source_id):
    try:
        source_repository.delete_by_name(source_id)
    except Exception as e:
        return str(e), 400
    return 'Delete source'
