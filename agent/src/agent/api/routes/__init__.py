from flask import jsonify

import agent.destination


def needs_destination(func):
    if not agent.destination.HttpDestination.exists():
        def foo():
            return jsonify('Destination is not configured. Please create agent destination first'), 400
        return foo
    return func
