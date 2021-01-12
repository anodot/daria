import agent
import agent.destination
import agent.pipeline

from functools import wraps
from flask import jsonify


def check_prerequisites(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        errors = agent.check_prerequisites()
        if errors:
            return jsonify(errors), 400
        return func(*args, **kwargs)
    return wrapper


def needs_pipeline(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        pipeline_id = kwargs['pipeline_name']
        if not agent.pipeline.repository.exists(pipeline_id):
            return jsonify(f'Pipeline {pipeline_id} does not exist'), 400
        return func(*args, **kwargs)
    return wrapper
