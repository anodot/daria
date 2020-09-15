import traceback

from agent import pipeline
from agent.modules import anodot_api_client
from agent.modules.logger import get_logger

logger = get_logger(__name__)

# note that pipelines might have different destinations in future
# so we'll need different clients for them
try:
    api_client = anodot_api_client.get_client()
    for pipeline_ in pipeline.repository.get_all():
        api_client.send_pipeline_data_to_bc(pipeline.transform_for_bc(pipeline_))
except Exception:
    logger.error(traceback.format_exc())
