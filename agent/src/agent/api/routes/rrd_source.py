from flask import jsonify, Blueprint, request
from agent import pipeline, data_extractor
from agent.api.routes import needs_pipeline

rrd_source = Blueprint('rrd_source', __name__)


@rrd_source.route('/rrd_source/fetch_data/<pipeline_id>', methods=['GET'])
@needs_pipeline
def read(pipeline_id: str):
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    metrics = data_extractor.rrd.extract_metrics(
        pipeline_,
        str(request.args['start']),
        str(request.args['end']),
        str(request.args['step']),
    )
    return jsonify(metrics)
