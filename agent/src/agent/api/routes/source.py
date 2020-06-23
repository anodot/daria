from flask import jsonify, Blueprint, request
from agent import source
from agent.api.forms import source as source_form
from agent.destination import HttpDestination
from agent.repository import source_repository

sources = Blueprint('test', __name__)


class RequestException(Exception):
    pass


def __transform(data: dict) -> dict:
    return {'name': data.pop('name'), 'type': data.pop('type'), 'config': data}


def __validate_request():
    errors = []
    if not HttpDestination.exists():
        errors.append('Destination is not configured. Please create agent destination first')
    source_type = request.get_json().get('type')
    if not source_type:
        errors.append('Please, specify the source type')
    elif source_type not in source.types:
        errors.append(f'Source type is invalid, available types are {", ".join(source.types)}')
    name = request.get_json().get('name')
    if not name:
        errors.append('Please, specify the source name')
    elif source_repository.exists(request.get_json()['name']):
        errors.append(f'Source {name} already exists')
    if errors:
        raise RequestException(errors)


@sources.route('/sources', methods=['GET'])
def list_sources():
    return jsonify(source_repository.get_all())


@sources.route('/sources', methods=['POST'])
def create():
    try:
        __validate_request()
    except RequestException as e:
        return str(e), 400
    form = source_form.get_form(request.get_json().get('type'), source_form.FormType.CREATE)\
        .from_json(request.get_json())
    if not form.validate():
        return form.errors, 400
    try:
        source_instance = source.create_from_json(__transform(request.get_json()))
    except Exception as e:
        return str(e)
    return source_instance.to_dict()


@sources.route('/sources', methods=['PUT'])
def edit():
    try:
        __validate_request()
    except RequestException as e:
        return str(e), 400
    form = source_form.get_form(request.get_json()['type'], source_form.FormType.EDIT)
    if not form.validate():
        return form.errors, 400
    try:
        source_instance = source.edit_using_json(__transform(request.get_json()))
    except Exception as e:
        return str(e)
    return source_instance.to_dict()


@sources.route('/sources/<source_id>', methods=['DELETE'])
def delete(source_id):
    try:
        source_repository.delete_by_name(source_id)
    except Exception as e:
        return str(e)
    return 'Delete source'
