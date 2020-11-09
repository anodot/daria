import jsonschema
import agent.streamsets as stream_sets

from jsonschema import ValidationError
from flask import jsonify, Blueprint, request
from agent.modules import logger, constants

streamsets = Blueprint('streamsets', __name__)
logger = logger.get_logger(__name__)


def validate_configs(configs: list):
    json_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'source': {'url': 'string', 'username': 'string', 'password': 'string'},
            },
            'required': ['url']
        }
    }
    jsonschema.validate(configs, json_schema)


def validate_configs_for_edit(configs: list):
    json_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'source': {'url': 'string', 'username': 'string', 'password': 'string'},
            },
            'required': ['url', 'username', 'password']
        }
    }
    jsonschema.validate(configs, json_schema)


def validate_configs_for_delete(configs: list):
    json_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'source': {'url': 'string'},
            },
            'required': ['url']
        }
    }
    jsonschema.validate(configs, json_schema)


@streamsets.route('/streamsets', methods=['GET'])
def list_streamsets():
    return jsonify(stream_sets.repository.get_all_names())


@streamsets.route('/streamsets', methods=['POST'])
def add():
    configs = request.get_json()
    try:
        validate_configs(configs)
    except ValidationError as e:
        return jsonify(str(e)), 400
    for config in configs:
        streamsets_ = stream_sets.StreamSets(
            config['url'],
            config.get('username', constants.DEFAULT_STREAMSETS_USERNAME),
            config.get('password', constants.DEFAULT_STREAMSETS_PASSWORD),
        )
        try:
            stream_sets.validator.validate(streamsets_)
        except stream_sets.validator.ValidationException as e:
            return jsonify(str(e)), 400
        stream_sets.manager.create_streamsets(streamsets_)
    return jsonify('')


@streamsets.route('/streamsets', methods=['PUT'])
def edit():
    configs = request.get_json()
    try:
        validate_configs_for_edit(configs)
    except ValidationError as e:
        return jsonify(str(e)), 400
    for config in configs:
        try:
            streamsets_ = stream_sets.repository.get_by_url(config['url'])
        except stream_sets.repository.StreamsetsNotExistsException as e:
            return jsonify(str(e)), 400
        streamsets_.username = config['username']
        streamsets_.password = config['password']
        try:
            stream_sets.validator.validate(streamsets_)
        except stream_sets.validator.ValidationException as e:
            return jsonify(str(e)), 400
        stream_sets.repository.save(streamsets_)
    return jsonify('')


@streamsets.route('/streamsets', methods=['DELETE'])
def delete():
    configs = request.get_json()
    try:
        validate_configs_for_delete(configs)
    except ValidationError as e:
        return jsonify(str(e)), 400
    try:
        for config in configs:
            stream_sets.manager.delete_streamsets(
                stream_sets.repository.get_by_url(config['url'])
            )
    except (stream_sets.repository.StreamsetsNotExistsException, stream_sets.manager.StreamsetsException) as e:
        return jsonify(str(e)), 400
    return jsonify('')


@streamsets.route('/streamsets/balance', methods=['DELETE'])
def balance():
    stream_sets.manager.StreamsetsBalancer().balance()
    return '', 200
