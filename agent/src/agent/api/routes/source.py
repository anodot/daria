from flask import jsonify, Blueprint, request
from agent.api import routes
from jsonschema import ValidationError
from agent import source, check_prerequisites

sources = Blueprint('test', __name__)


@sources.route('/sources', methods=['GET'])
def list_sources():
    return jsonify(source.repository.get_all_names())


@sources.route('/sources', methods=['POST'])
@routes.needs_destination
def create():
    errors = check_prerequisites()
    if errors:
        return jsonify(errors), 400
    try:
        sources_ = source.manager.create_from_json(request.get_json())
    except (ValidationError, ValueError, source.SourceException) as e:
        return jsonify(str(e)), 400
    return jsonify(list(map(lambda x: x.to_dict(), sources_)))


@sources.route('/sources', methods=['PUT'])
def edit():
    errors = check_prerequisites()
    if errors:
        return jsonify(errors), 400
    try:
        sources_ = source.manager.edit_using_json(request.get_json())
    except (ValidationError, source.SourceException, ValueError) as e:
        return jsonify(str(e)), 400
    return jsonify(list(map(lambda x: x.to_dict(), sources_)))


@sources.route('/sources/<source_id>', methods=['DELETE'])
def delete(source_id):
    try:
        source.repository.delete_by_name(source_id)
    except (source.repository.SourceNotExists, source.SourceException) as e:
        return jsonify(str(e)), 400
    return jsonify('')
