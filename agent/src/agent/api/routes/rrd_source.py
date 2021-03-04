from flask import jsonify, Blueprint, request
from agent import pipeline, source
from agent.api.routes import needs_pipeline

rrd_source = Blueprint('test', __name__)


@rrd_source.route('/rrd_source/fetch_data/<pipeline_id>', methods=['POST'])
@needs_pipeline
def read(pipeline_id: str):
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    metrics = source.rrd.extract_metrics(
        pipeline_.source,
        str(request.get_json()['start']),
        str(request.get_json()['end']),
        str(request.get_json()['step']),
        pipeline_.config['exclude_datasources'],
        pipeline_.config['exclude_hosts'],
    )
    return jsonify(metrics)
