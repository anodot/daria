from flask import jsonify, Blueprint, request
from agent import source
from agent.api.forms.source import forms
from agent.destination import HttpDestination
from agent.repository import source_repository
from agent.api.transformers import source as source_transformers

sources = Blueprint('test', __name__)


def universal_transform(data: dict) -> dict:
    return {'name': data.pop('name'), 'type': data.pop('type'), 'config': data}


@sources.route('/sources', methods=['GET'])
def list_sources():
    return jsonify(source_repository.get_all())


@sources.route('/sources', methods=['POST'])
def create():
    if not HttpDestination.exists():
        return 'Destination is not configured. Please create agent destination first', 400
    source_type = request.get_json().get('type')
    if not source_type:
        return "Please, specify the source type", 400
    if source_type not in forms:
        types = ', '.join(forms)
        return f'Source type is invalid, available types are {types}'
    form = forms[source_type].from_json(request.get_json())
    if not form.validate():
        return form.errors, 400
    source_obj = source.create_from_json(
        # source_transformers.get_transformer(source_type)(request.get_json())
        universal_transform(request.get_json())
    )
    return source_obj.to_dict()


@sources.route('/sources/<source_id>', methods=['PUT'])
def edit(source_id):
    return 'Edit source'


@sources.route('/sources/<source_id>', methods=['DELETE'])
def delete(source_id):
    source_repository.delete_by_name(source_id)
    return 'Delete source'
