from flask import jsonify, Blueprint
from agent import pipeline, data_extractor
from agent.api.routes import needs_pipeline
from agent.data_extractor.snmp.snmp import SNMPError

snmp = Blueprint('snmp_source', __name__)


@snmp.route('/data_extractor/snmp/<pipeline_id>', methods=['GET'])
@needs_pipeline
def read(pipeline_id: str):
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    try:
        metrics = data_extractor.snmp.extract_metrics(pipeline_)
    except SNMPError as e:
        return jsonify(str(e)), 500
    return jsonify(metrics)
