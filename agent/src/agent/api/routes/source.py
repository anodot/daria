from flask import jsonify, Blueprint, request
from agent.api import routes
from jsonschema import ValidationError
from agent import source

sources = Blueprint('test', __name__)


@sources.route('/sources', methods=['GET'])
def list_sources():
    return jsonify(source.repository.get_all())


@sources.route('/sources', methods=['POST'])
@routes.needs_destination
def create():
    json = request.get_json()
    try:
        source.manager.validate_configs_for_create(json)
        source_instances = []
        for config in json:
            source_instances.append(source.manager.create_from_json(config).to_dict())
    except (ValidationError, ValueError, source.SourceException) as e:
        return jsonify(str(e)), 400
    return jsonify(source_instances)


@sources.route('/sources', methods=['PUT'])
def edit():
    try:
        source.manager.validate_configs_for_edit(request.get_json())
        source_instances = []
        for config in request.get_json():
            source_instances.append(source.manager.edit_using_json(config).to_dict())
    except (ValidationError, ValueError) as e:
        return jsonify(str(e)), 400
    return jsonify(source_instances)


@sources.route('/sources/<source_id>', methods=['DELETE'])
def delete(source_id):
    try:
        source.repository.delete_by_name(source_id)
    except (source.repository.SourceNotExists, source.SourceException) as e:
        return jsonify(str(e)), 400
    return jsonify('')
