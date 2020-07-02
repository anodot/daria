from functools import wraps

import agent.destination

from flask import jsonify
from agent.repository import pipeline_repository


def needs_destination(func):
    if not agent.destination.HttpDestination.exists():
        def foo():
            return jsonify('Destination is not configured. Please create agent destination first'), 400
        return foo
    return func


def needs_pipeline(func):
    @wraps(func)
    def wrapper(**kwargs):
        pipeline_id = kwargs['pipeline_id']
        if not pipeline_repository.exists(pipeline_id):
            return jsonify(f'Pipeline {pipeline_id} does not exist'), 400
        return func
    return wrapper
