from agent.scripts import kafka_topology
from flask import Blueprint, request

scripts = Blueprint('scripts', __name__)


@scripts.route('/scripts/kafkatopology', methods=['GET'])
def kafkatopology():
    kafka_topology.run()

