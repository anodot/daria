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


def get_config_validator(source_type: str) -> Validator:
    jdbc_sources = [
        source.TYPE_DATABRICKS, source.TYPE_MYSQL, source.TYPE_POSTGRES, source.TYPE_CLICKHOUSE, source.TYPE_ORACLE
    ]

    if source_type == source.TYPE_ELASTIC:
        return ElasticValidator()
    elif source_type in jdbc_sources:
        return JDBCValidator()
    return Validator()


class ValidationException(Exception):
    pass
