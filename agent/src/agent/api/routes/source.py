from flask import jsonify, Blueprint
from agent.repository import source_repository

source = Blueprint('test', __name__)


@source.route('/sources', methods=['GET'])
def list_sources():
    sources = []
    for s in source_repository.get_all():
        sources.append(s)
    return jsonify(sources)


@source.route('/sources', methods=['POST'])
def create():
    return 'Create a source'


@source.route('/source/<source_id>', methods=['PUT'])
def edit(source_id):
    return 'Edit source'


@source.route('/source/<source_id>', methods=['DELETE'])
def delete(source_id):
    return 'Delete source'
