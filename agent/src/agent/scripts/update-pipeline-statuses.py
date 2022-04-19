import traceback
import sdc_client

from agent import pipeline, di, monitoring
from agent.modules import logger

di.init()
logger = logger.get_logger(__name__)


def main():
    try:
        statuses = sdc_client.get_all_pipeline_statuses()
        for pipeline_ in pipeline.repository.get_all():
            if pipeline_.name in statuses:
                pipeline_.status = statuses[pipeline_.name]['status']
                pipeline.repository.save(pipeline_)
    except Exception:
        monitoring.metrics.SCHEDULED_SCRIPTS_ERRORS.labels('update-pipeline-statuses.py').inc(1)
        logger.error(traceback.format_exc())


if __name__ == '__main__':
    main()
