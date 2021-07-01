from flask import jsonify, Blueprint, request
from agent import pipeline, data_extractor
from agent.api.routes import needs_pipeline

snmp = Blueprint('snmp_source', __name__)


# todo data_extractor or source?
@snmp.route('/data_extractor/snmp/<pipeline_id>', methods=['GET'])
@needs_pipeline
def read(pipeline_id: str):
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    metrics = data_extractor.snmp.extract_metrics(pipeline_)
    return jsonify(metrics)
