from flask import Blueprint
from flask import request

destination = Blueprint('destination', __name__)


@destination.route('/bye', methods=['GET'])
def create():
    return 'Bye world!'


@destination.route('/dust', methods=['POST', 'GET'])
def foo():
    data = request.args
    return data


# @destination.route('/destination', methods=['PUT'])
# def edit():
#     return 'Edit destination'
#
#
# @destination.route('/destination', methods=['DELETE'])
# def delete():
#     return 'Delete destination'
