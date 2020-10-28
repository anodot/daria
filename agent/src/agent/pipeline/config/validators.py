import click

from agent.pipeline.elastic import query_validator
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
        errors = query_validator.get_errors(query, pipeline.source.config[source.ElasticSource.CONFIG_OFFSET_FIELD])
        if errors:
            raise click.ClickException(errors)


class JDBCValidator(BaseValidator):
    @staticmethod
    def validate(pipeline):
        if source.JDBCSource.TIMESTAMP_CONDITION not in pipeline.query:
            raise click.ClickException(f'Please add {source.JDBCSource.TIMESTAMP_CONDITION} constant to the query')


def get_config_validator(pipeline: p.Pipeline) -> BaseValidator:
    if pipeline.source.type == source.TYPE_ELASTIC:
        return ElasticValidator()
    if pipeline.source.type in [source.TYPE_MYSQL, source.TYPE_POSTGRES]:
        return JDBCValidator()
    return BaseValidator()
