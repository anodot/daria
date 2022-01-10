from agent.pipeline import Pipeline
from agent.pipeline.validators import elastic_query, jdbc_query
from agent import source


class Validator:
    @staticmethod
    def validate(pipeline):
        pass


class ElasticValidator(Validator):
    @staticmethod
    def validate(pipeline):
        with open(pipeline.config['query_file']) as f:
            query = f.read()
        errors = elastic_query.get_errors(query, pipeline.source.config[source.ElasticSource.CONFIG_OFFSET_FIELD])
        if errors:
            raise ValidationException(errors)


class JDBCValidator(Validator):
    @staticmethod
    def validate(pipeline):
        errors = jdbc_query.get_errors(pipeline.query)
        if errors:
            raise ValidationException(errors)


class ObserviumValidator(Validator):
    @staticmethod
    def validate(pipeline: Pipeline):
        errors = []
        if pipeline.dimension_configurations:
            diff = pipeline.dimensions - pipeline.dimension_configurations.keys()
            if diff:
                errors.append(f'These dimensions don\'t have a configuration: {",".join(diff)}')
            reverse_diff = pipeline.dimension_configurations.keys() - pipeline.dimensions
            if reverse_diff:
                errors.append(
                    f'Extra dimension configurations provided that are not in the dimensions list: {",".join(reverse_diff)}'
                )
        if errors:
            raise ValidationException(errors)


def get_config_validator(source_type: str) -> Validator:
    jdbc_sources = [
        source.TYPE_DATABRICKS, source.TYPE_MYSQL, source.TYPE_POSTGRES, source.TYPE_CLICKHOUSE, source.TYPE_ORACLE
    ]

    if source_type == source.TYPE_ELASTIC:
        return ElasticValidator()
    elif source_type in jdbc_sources:
        return JDBCValidator()
    elif source_type == source.TYPE_OBSERVIUM:
        return ObserviumValidator()
    return Validator()


class ValidationException(Exception):
    pass
