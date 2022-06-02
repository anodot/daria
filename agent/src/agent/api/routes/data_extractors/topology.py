from flask import jsonify, Blueprint, request
from agent import pipeline, data_extractor
from agent.api.routes import needs_pipeline

topology = Blueprint('topology_source', __name__)


@topology.route('/data_extractors/topology/<pipeline_id>', methods=['POST'])
@needs_pipeline
def read(pipeline_id: str):
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    metrics = data_extractor.topology.transform_metrics(pipeline_, request.json)
    return jsonify(metrics)
