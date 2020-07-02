from typing import Callable

from flask import jsonify, Response

import agent.destination


def needs_destination(func):
    if not agent.destination.HttpDestination.exists():
        def foo():
            return 'Destination is not configured. Please create agent destination first', 400
        return foo
    return func


def create(validate_json_for_create: Callable, create_from_json: Callable, json: dict) -> (Response, int):
    try:
        validate_json_for_create(json)
        source_instances = []
        for config in json:
            source_instances.append(create_from_json(config).to_dict())
    except Exception as e:
        return jsonify(str(e)), 400
    return jsonify(source_instances)
