from flask import jsonify, Blueprint, request
from prometheus_client import generate_latest, Info
from agent import version


monitoring = Blueprint('monitoring', __name__)


VERSION = Info('version', 'Agent version')
VERSION.info({'version': version.__version__, 'build_time': version.__build_time__, 'git_sha1': version.__git_sha1__})




@monitoring.route('/metrics', methods=['GET'])
def metrics():
    return jsonify(generate_latest())
