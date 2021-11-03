import requests
import sdc_client

from jsonschema import ValidationError
from agent.api.routes import needs_pipeline
from flask import jsonify, Blueprint, request, escape
from agent.api import routes
from agent import pipeline, source, streamsets, monitoring
from agent.modules import logger
from sdc_client import Severity

pipelines = Blueprint('pipelines', __name__)
logger = logger.get_logger(__name__)


@pipelines.route('/pipelines', methods=['GET'])
def list_pipelines():
    return jsonify([p.to_dict() for p in pipeline.repository.get_all()])


@pipelines.route('/pipelines/<pipeline_id>', methods=['GET'])
def get_pipeline_config(pipeline_id: str):
    return jsonify(pipeline.repository.get_by_id(pipeline_id).to_dict())


@pipelines.route('/pipelines', methods=['POST'])
@routes.check_pipeline_prerequisites
def create():
    try:
        pipelines_ = pipeline.json_builder.build_multiple(request.get_json())
    except (ValidationError, source.SourceNotExists, requests.exceptions.ConnectionError) as e:
        return jsonify(str(e)), 400
    except (pipeline.PipelineException, streamsets.manager.StreamsetsException) as e:
        return jsonify(str(e)), 500
    return jsonify(list(map(lambda x: x.to_dict(), pipelines_)))


@pipelines.route('/pipelines', methods=['PUT'])
@routes.check_pipeline_prerequisites
def edit():
    try:
        pipelines_ = pipeline.json_builder.edit_multiple(request.get_json())
    except ValueError as e:
        return jsonify(str(e)), 400
    except (pipeline.PipelineException, streamsets.manager.StreamsetsException) as e:
        return jsonify(str(e)), 500
    return jsonify(list(map(lambda x: x.to_dict(), pipelines_)))


@pipelines.route('/pipelines/<pipeline_id>', methods=['DELETE'])
@needs_pipeline
def delete(pipeline_id: str):
    pipeline.manager.delete_by_id(pipeline_id)
    return jsonify('')


@pipelines.route('/pipelines/force-delete/<pipeline_id>', methods=['DELETE'])
@needs_pipeline
def force_delete(pipeline_id: str):
    return jsonify(pipeline.manager.force_delete(pipeline_id))


@pipelines.route('/pipelines/<pipeline_id>/start', methods=['POST'])
@needs_pipeline
def start(pipeline_id: str):
    try:
        pipeline.manager.start(pipeline.repository.get_by_id(pipeline_id))
    except sdc_client.PipelineFreezeException as e:
        return jsonify(str(e)), 400
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_id>/stop', methods=['POST'])
@needs_pipeline
def stop(pipeline_id: str):
    try:
        sdc_client.stop(pipeline.repository.get_by_id(pipeline_id))
    except sdc_client.ApiClientException as e:
        return jsonify(str(e)), 400
    except sdc_client.PipelineFreezeException as e:
        return jsonify(str(e)), 400
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_id>/force-stop', methods=['POST'])
@needs_pipeline
def force_stop(pipeline_id: str):
    try:
        sdc_client.force_stop(pipeline.repository.get_by_id(pipeline_id))
    except sdc_client.PipelineFreezeException as e:
        return jsonify(str(e)), 400
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_id>/info', methods=['GET'])
@needs_pipeline
def info(pipeline_id: str):
    number_of_history_records = int(request.args.get('number_of_history_records', 10))
    try:
        return jsonify(
            sdc_client.get_pipeline_info(pipeline.repository.get_by_id(pipeline_id), number_of_history_records)
        )
    except sdc_client.ApiClientException as e:
        return jsonify(str(e)), 500


@pipelines.route('/pipelines/<pipeline_id>/logs', methods=['GET'])
@needs_pipeline
def logs(pipeline_id: str):
    if 'severity' in request.args and request.args['severity'] not in pipeline.manager.LOG_LEVELS:
        return f'{escape(request.args["severity"])} logging level is not one of {", ".join(pipeline.manager.LOG_LEVELS)}', 400
    severity = Severity[request.args.get('severity', Severity.INFO.value)]
    number_of_records = int(request.args.get('number_of_records', 10))
    try:
        return jsonify(
            sdc_client.get_pipeline_logs(pipeline.repository.get_by_id(pipeline_id), severity, number_of_records)
        )
    except sdc_client.ApiClientException as e:
        return jsonify(str(e)), 500


@pipelines.route('/pipelines/<pipeline_id>/enable-destination-logs', methods=['POST'])
@needs_pipeline
def enable_destination_logs(pipeline_id: str):
    pipeline.manager.enable_destination_logs(pipeline.repository.get_by_id(pipeline_id))
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_id>/disable-destination-logs', methods=['POST'])
@needs_pipeline
def disable_destination_logs(pipeline_id: str):
    pipeline.manager.disable_destination_logs(pipeline.repository.get_by_id(pipeline_id))
    return jsonify('')


@pipelines.route('/pipelines/<pipeline_id>/reset', methods=['POST'])
@needs_pipeline
def reset(pipeline_id: str):
    try:
        pipeline.manager.reset(pipeline.repository.get_by_id(pipeline_id))
    except sdc_client.ApiClientException as e:
        return jsonify(str(e)), 500
    return jsonify('')


@pipelines.route('/pipeline-status-change/<pipeline_id>', methods=['POST'])
def pipeline_status_change(pipeline_id: str):
    data = request.get_json()
    status = data['pipeline_status']
    pipeline_ = pipeline.repository.get_by_id(pipeline_id)

    if status == pipeline.Pipeline.STATUS_RUNNING_ERROR:
        pipeline.manager.increase_retry_counter(pipeline_)

    pipeline_.status = status
    pipeline.repository.save(pipeline_)
    labels = (pipeline_.streamsets.url, pipeline_.name, pipeline_.source.type)
    monitoring.metrics.PIPELINE_STATUS.labels(*labels).state(pipeline_.status)
    return jsonify('')


@pipelines.route('/pipeline-offset/<pipeline_id>', methods=['POST'])
@needs_pipeline
def pipeline_offset_changed(pipeline_id: str):
    pipeline.manager.update_pipeline_offset(
        pipeline.repository.get_by_id(pipeline_id),
        float(request.get_json()['offset'])
    )
    return jsonify('')
