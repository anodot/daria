import agent.destination
import agent.pipeline

from functools import wraps
from flask import jsonify


def needs_destination(func):
    if not agent.destination.destination.HttpDestination.exists():
        def foo():
            return jsonify('Destination is not configured. Please create agent destination first'), 400
        return foo
    return func


def needs_pipeline(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        pipeline_id = kwargs['pipeline_id']
        if not agent.pipeline.repository.exists(pipeline_id):
            return jsonify(f'Pipeline {pipeline_id} does not exist'), 400
        return func(*args, **kwargs)
    return wrapper
