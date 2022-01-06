from flask import jsonify, Blueprint
from agent import pipeline, data_extractor
from agent.api.routes import needs_pipeline

observium = Blueprint('observium_source', __name__)


@observium.route('/data_extractors/observium/<pipeline_id>', methods=['GET'])
@needs_pipeline
def read(pipeline_id: str):
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    metrics = data_extractor.observium.extract_metrics(pipeline_)
    return jsonify(metrics)
