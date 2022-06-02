from agent.pipeline import Pipeline
from agent.pipeline.config import validators
from agent.pipeline.validators import elastic_query, jdbc_query
from agent import source, pipeline


class Validator:
    @staticmethod
    def validate(pipeline_):
        pass


class ElasticValidator(Validator):
    @staticmethod
    def validate(pipeline_):
        if 'query_file' in pipeline_.config:
            with open(pipeline_.config['query_file']) as f:
                query = f.read()
        elif 'query' in pipeline_.config:
            query = pipeline_.config['query']
        else:
            raise ValidationException('No query or query_file')
        if errors := elastic_query.get_errors(query, pipeline_.source.config[source.ElasticSource.CONFIG_OFFSET_FIELD]):
            raise ValidationException(errors)


class JDBCValidator(Validator):
    @staticmethod
    def validate(pipeline_):
        if errors := jdbc_query.get_errors(pipeline_.query):
            raise ValidationException(errors)


def get_config_validator(pipeline_: Pipeline) -> Validator:
    jdbc_sources = [
        source.TYPE_DATABRICKS,
        source.TYPE_MYSQL,
        source.TYPE_MSSQL,
        source.TYPE_POSTGRES,
        source.TYPE_CLICKHOUSE,
        source.TYPE_ORACLE,
    ]

    if isinstance(pipeline_, pipeline.TopologyPipeline):
        return validators.TopologyValidator()
    if pipeline_.source.type == source.TYPE_ELASTIC:
        return ElasticValidator()
    if pipeline_.source.type in jdbc_sources:
        return JDBCValidator()
    return Validator()


class ValidationException(Exception):
    pass
