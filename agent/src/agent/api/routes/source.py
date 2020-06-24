from flask import jsonify, Blueprint, request
from agent import source
from agent.api.forms import source as source_form
from agent.api import transformers
from agent.destination import HttpDestination
from agent.repository import source_repository

sources = Blueprint('test', __name__)


class RequestException(Exception):
    pass


def __validate_base():
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
    return errors


def __validate_create():
    errors = __validate_base()
    name = request.get_json()['name']
    if source_repository.exists(name):
        errors.append(f'Source {name} already exists')
    if errors:
        raise RequestException(errors)


def __validate_edit():
    errors = __validate_base()
    name = request.get_json()['name']
    if name and not source_repository.exists(name):
        errors.append(f'Source {name} does not exist')
    if errors:
        raise RequestException(errors)


@sources.route('/sources', methods=['GET'])
def list_sources():
    return jsonify(source_repository.get_all())


@sources.route('/sources', methods=['POST'])
def create():
    try:
        __validate_create()
    except RequestException as e:
        return str(e), 400
    source_type = request.get_json()['type']
    form = source_form.get_form(source_type, source_form.FormType.CREATE).from_json(request.get_json())
    if not form.validate():
        return form.errors, 400
    try:
        source_instance = source.create_from_json(transformers.get_transformer(source_type)(request.get_json()))
    except Exception as e:
        return str(e), 400
    return source_instance.to_dict()


@sources.route('/simple-sources', methods=['POST'])
def simple_create():
    try:
        __validate_create()
    except RequestException as e:
        return str(e), 400
    try:
        source_instance = source.create_from_json(request.get_json())
    except Exception as e:
        return str(e), 400
    return source_instance.to_dict()


@sources.route('/simple-sources', methods=['PUT'])
def simple_edit():
    try:
        __validate_edit()
    except RequestException as e:
        return str(e), 400
    try:
        source_instance = source.edit_using_json(request.get_json())
    except Exception as e:
        return str(e), 400
    return source_instance.to_dict()


@sources.route('/sources', methods=['PUT'])
def edit():
    try:
        __validate_edit()
    except RequestException as e:
        return str(e), 400
    source_type = request.get_json()['type']
    form = source_form.get_form(source_type, source_form.FormType.EDIT).from_json(request.get_json())
    if not form.validate():
        return form.errors, 400
    try:
        # как должен работать edit файлом? редактируем все? а что если только одно поле указать?
        source_instance = source.edit_using_json(transformers.get_transformer(source_type)(request.get_json()))
    except Exception as e:
        return str(e), 400
    return source_instance.to_dict()


@sources.route('/sources/<source_id>', methods=['DELETE'])
def delete(source_id):
    try:
        source_repository.delete_by_name(source_id)
    except Exception as e:
        return str(e), 400
    return 'Delete source'
