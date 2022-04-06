from agent import monitoring
from agent.modules import logger, field, lookup
from agent.modules.mysql import MySQL
from agent.pipeline import Pipeline, jdbc

logger_ = logger.get_logger(__name__)

N_REQUESTS_TRIES = 3


def extract_metrics(pipeline_: Pipeline, offset: int) -> list:
    with lookup.Provide(pipeline_.lookups):
        return _create_metrics(_get(pipeline_, offset), pipeline_)


def _get(pipeline_: Pipeline, offset: int):
    try:
        return MySQL(
            pipeline_.source.config['host'],
            pipeline_.source.config.get('port', '3306'),
            pipeline_.source.config.get('username'),
            pipeline_.source.config.get('password'),
            pipeline_.source.config['database'],
        ).execute(_build_query(pipeline_, offset))
    except Exception as e:
        monitoring.metrics.SOURCE_MYSQL_ERRORS.labels(pipeline_.name).inc(1)
        logger_.error(str(e))
        raise


def _build_query(pipeline_: Pipeline, offset: int):
    timestamp_condition = (
        f'{pipeline_.timestamp_path} >= {offset - pipeline_.interval} and {pipeline_.timestamp_path} < {offset}'
    )
    return pipeline_.query.replace(jdbc.query.TIMESTAMP_CONDITION, timestamp_condition)


def _create_metrics(data: dict, pipeline_: Pipeline) -> list:
    metrics = []
    # these values must be outside the for loop for optimization purposes
    fields_dims = field.build_fields(pipeline_.dimension_configurations)
    fields_meas = field.build_fields(pipeline_.measurement_configurations)
    fields_tags = field.build_fields(pipeline_.tag_configurations)
    schema_id = pipeline_.get_schema_id()
    try:
        for obj in data:
            metric = {
                "timestamp": obj[pipeline_.timestamp_name],
                "dimensions": field.extract_fields(fields_dims, obj),
                "measurements": field.extract_fields(fields_meas, obj, True),
                "tags": {name: [tags]
                         for name, tags in field.extract_fields(fields_tags, obj).items()},
                "schemaId": schema_id,
            }
            metrics.append(metric)
    except NoMeasurementException as e:
        message = f'[{pipeline_.name}] - These values were not extracted from data: {e}'
        if pipeline_.is_strict:
            raise Exception(message) from e
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
