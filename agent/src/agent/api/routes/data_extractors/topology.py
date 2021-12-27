from flask import jsonify, Blueprint
from agent import pipeline, data_extractor
from agent.api.routes import needs_pipeline

topology = Blueprint('topology_source', __name__)


@topology.route('/data_extractor/topology/<pipeline_id>', methods=['GET'])
@needs_pipeline
def read(pipeline_id: str):
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    metrics = data_extractor.topology.extract_metrics(pipeline_)
    return jsonify(metrics)
