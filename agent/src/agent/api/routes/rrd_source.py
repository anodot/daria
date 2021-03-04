from flask import jsonify, Blueprint, request
from agent import pipeline, source
from agent.api.routes import needs_pipeline

rrd_source = Blueprint('test', __name__)


@rrd_source.route('/rrd_source/read/<pipeline_id>', methods=['POST'])
@needs_pipeline
def read(pipeline_id: str):
    metrics = source.rrd.extract_metrics(
        pipeline.repository.get_by_id(pipeline_id).source,
        str(request.get_json()['start']),
        str(request.get_json()['end']),
        str(request.get_json()['step']),
    )
    return jsonify(metrics)
