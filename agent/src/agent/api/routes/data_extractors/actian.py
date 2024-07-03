from flask import jsonify, Blueprint, request
from agent import pipeline, data_extractor
from agent.api.routes import needs_pipeline

cacti = Blueprint('cacti_source', __name__)


@cacti.route('/data_extractor/actian/<pipeline_id>', methods=['GET'])
@needs_pipeline
def read(pipeline_id: str):
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    offset = request.args.get('offset')
    if not offset:
        return jsonify('No offset provided'), 400
    metrics = data_extractor.actian.extract_metrics(pipeline_, int(offset))
    return jsonify(metrics)
