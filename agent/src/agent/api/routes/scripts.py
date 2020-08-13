import jsonschema
from agent.scripts import kafka_topology
from flask import Blueprint, request, jsonify

scripts = Blueprint('scripts', __name__)


@scripts.route('/scripts/kafka_topology', methods=['POST'])
def kafkatopology():
    request_schema = {
        'type': 'object',
        'properties': {
            'topic': {"type": "string"},
            'file_type': {"type": "string"},
            'brokers': {"type": "array", "items": {"type": "string"}},
        },
        'required': ['topic', 'file_type', 'brokers']
    }
    params = request.json
    try:
        jsonschema.validate(params, request_schema)
    except jsonschema.ValidationError as e:
        return jsonify(str(e)), 400
    kafka_topology.run(**params)
    return jsonify('')
