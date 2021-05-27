from copy import deepcopy
from agent import pipeline, source, di
from agent.modules import logger

logger_ = logger.get_logger('scripts.upgrade.3.13.0', stdout=True)
di.init()

for pipeline_ in pipeline.repository.get_by_type(source.TYPE_INFLUX):
    logger_.info(f'Updating `{pipeline_.name}` pipeline')

    values = {}
    config = deepcopy(pipeline_.config)
    for value in config['value']['values']:
        values[value] = config.get("target_type", "gauge")
    config['values'] = values
    del config['value']
    pipeline_.set_config(config)
    pipeline.manager.update(pipeline_)
    pipeline.repository.save(pipeline_)

    logger_.info('Done')

logger_.info('Finished influx pipelines update')
