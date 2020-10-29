import click

from agent.pipeline.validators import elastic_query, jdbc_query
from agent import source
from agent.pipeline import pipeline as p


class BaseValidator:
    @staticmethod
    def validate(pipeline):
        pass


class ElasticValidator(BaseValidator):
    @staticmethod
    def validate(pipeline):
        with open(pipeline.config['query_file']) as f:
            query = f.read()
        errors = elastic_query.get_errors(query, pipeline.source.config[source.ElasticSource.CONFIG_OFFSET_FIELD])
        if errors:
            raise click.ClickException(errors)


class JDBCValidator(BaseValidator):
    @staticmethod
    def validate(pipeline):
        errors = jdbc_query.get_errors(pipeline.query)
        if errors:
            raise click.ClickException(errors)


def get_config_validator(pipeline: p.Pipeline) -> BaseValidator:
    if pipeline.source.type == source.TYPE_ELASTIC:
        return ElasticValidator()
    if pipeline.source.type in [source.TYPE_MYSQL, source.TYPE_POSTGRES]:
        return JDBCValidator()
    return BaseValidator()
