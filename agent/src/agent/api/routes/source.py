from flask import jsonify, Blueprint, request
from agent.api import routes
from jsonschema import ValidationError
from agent import source

sources = Blueprint('test', __name__)


@sources.route('/sources', methods=['GET'])
def list_sources():
    return jsonify(source.repository.get_all_names())


@sources.route('/sources', methods=['POST'])
@routes.check_source_prerequisites
def create():
    try:
        sources_ = source.json_builder.build_multiple(request.get_json())
    except (ValidationError, ValueError, source.SourceException) as e:
        return jsonify(str(e)), 400
    return jsonify(list(map(lambda x: x.to_dict(), sources_)))


@sources.route('/sources', methods=['PUT'])
@routes.check_source_prerequisites
def edit():
    try:
        sources_ = source.json_builder.edit_multiple(request.get_json())
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


@sources.route('/sources/<source_id>', methods=['GET'])
def get(source_id):
    try:
        config = source.repository.get_by_name(source_id).to_dict()
        with_credentials = request.args.get('with_credentials', default=False, type=bool)
        if not with_credentials:
            config = source.sensitive_data.mask(config)
    except (source.repository.SourceNotExists, source.SourceException) as e:
        return jsonify(str(e)), 400
    return jsonify(config)
