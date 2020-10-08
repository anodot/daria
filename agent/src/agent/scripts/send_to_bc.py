import traceback

from agent import pipeline, destination
from agent.destination.anodot_api_client import AnodotApiClient
from agent.modules.logger import get_logger

logger = get_logger(__name__)

try:
    api_client = AnodotApiClient(destination.repository.get())
    for pipeline_ in pipeline.repository.get_all():
        if pipeline_.name != pipeline.MONITORING:
            api_client.send_pipeline_data_to_bc(pipeline.manager.transform_for_bc(pipeline_))
except Exception:
    logger.error(traceback.format_exc())
