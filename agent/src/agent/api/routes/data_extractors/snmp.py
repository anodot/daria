from flask import jsonify, Blueprint
from agent import pipeline, data_extractor
from agent.api.routes import needs_pipeline

snmp = Blueprint('snmp_source', __name__)


@snmp.route('/data_extractor/snmp/<pipeline_id>', methods=['GET'])
@needs_pipeline
def read(pipeline_id: str):
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    metrics = data_extractor.snmp.extract_metrics(pipeline_)
    raise Exception('hey3')
    return jsonify(metrics)
