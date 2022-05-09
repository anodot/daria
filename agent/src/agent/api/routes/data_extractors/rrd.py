from flask import jsonify, Blueprint, request
from agent import pipeline, data_extractor
from agent.api.routes import needs_pipeline
from agent.modules import tools

rrd = Blueprint('rrd_source', __name__)


@rrd.route('/data_extractor/rrd/<pipeline_id>', methods=['GET'])
@needs_pipeline
def read(pipeline_id: str):
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)
    try:
        metrics = data_extractor.rrd.extract_metrics(
            pipeline_,
            str(request.args['start']),
            str(request.args['end']),
            str(request.args['step']),
        )
    except tools.ArchiveNotExistsException:
        return jsonify(''), 204
    return jsonify(metrics)
