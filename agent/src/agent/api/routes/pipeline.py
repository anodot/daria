from flask import jsonify, Blueprint, request
from agent import source
from agent.api.routes import needs_destination
from agent.repository import source_repository

destinations = Blueprint('destinations', __name__)


@destinations.route('/destinations', methods=['GET'])
def list_sources():
    return jsonify(source_repository.get_all())


@needs_destination
@destinations.route('/destinations', methods=['POST'])
def create():
    # if not HttpDestination.exists():
    #     return DESTINATION_DOESNT_EXIST, 400
    try:
        source.validate_json_for_create(request.get_json())
        source_instances = []
        for config in request.get_json():
            source_instances.append(source.create_from_json(config).to_dict())
    except Exception as e:
        return str(e), 400
    return jsonify(source_instances)


@destinations.route('/destinations', methods=['PUT'])
def edit():
    try:
        source.validate_json_for_edit(request.get_json())
        source_instances = []
        for config in request.get_json():
            source_instances.append(source.edit_using_json(config).to_dict())
    except Exception as e:
        return str(e), 400
    return jsonify(source_instances)


@destinations.route('/destinations/<destinations_id>', methods=['DELETE'])
def delete(destinations_id):
    try:
        source_repository.delete_by_name(destinations_id)
    except Exception as e:
        return str(e), 400
    return ''
