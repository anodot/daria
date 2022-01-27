from agent import monitoring
from agent.modules import logger, field, lookup
from agent.modules.mysql import MySQL
from agent.pipeline import Pipeline

logger_ = logger.get_logger(__name__)

N_REQUESTS_TRIES = 3


def extract_metrics(pipeline_: Pipeline) -> list:
    with lookup.Provide(pipeline_.lookups):
        return _create_metrics(_get(pipeline_), pipeline_)


def _get(pipeline_: Pipeline):
    try:
        return MySQL(
            pipeline_.source.config['host'],
            pipeline_.source.config.get('port', 3306),
            pipeline_.source.config.get('username'),
            pipeline_.source.config.get('password'),
            pipeline_.source.config['database'],
        ).execute(pipeline_.query)
    except Exception as e:
        monitoring.metrics.SOURCE_MYSQL_ERRORS.labels(pipeline_.name).inc(1)
        logger_.error(str(e))
        raise


def _create_metrics(data: dict, pipeline_: Pipeline) -> list:
    metrics = []
    # these values must be outside the for loop for optimization purposes
    fields = field.build_fields(pipeline_.dimension_configurations)
    value_paths = pipeline_.value_paths
    value_paths = dict(zip(value_paths, value_paths))
    schema_id = pipeline_.get_schema_id()
    try:
        for obj in data:
            metric = {
                "timestamp": obj[pipeline_.timestamp_name],
                "dimensions": field.extract_fields(fields, obj),
                "measurements": _extract_measurements(obj, value_paths),
                "schemaId": schema_id,
            }
            metrics.append(metric)
    except NoMeasurementException as e:
        message = f'[{pipeline_.name}] - These values were not extracted from data: {e}'
        if pipeline_.is_strict:
            raise Exception(message)
        else:
            logger_.warning(message)
    return metrics


def _extract_measurements(obj, value_paths):
    meas = {str(k): float(v) for k, v in obj.items() if str(k) in value_paths}
    if missed_measures := [v for v in value_paths.values() if v not in meas]:
        raise NoMeasurementException(", ".join(map(lambda s: f'`{s}`', missed_measures)))
    return meas


class NoMeasurementException(Exception):
    pass
