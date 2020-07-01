import click

from agent import source
from agent.pipeline.elastic import query_validator
from agent.source import ElasticSource
from agent.pipeline import Pipeline


class BaseValidator:
    @staticmethod
    def validate(pipeline):
        pass


class ElasticValidator(BaseValidator):
    @staticmethod
    def validate(pipeline):
        with open(pipeline.config['query_file']) as f:
            query = f.read()
        errors = query_validator.get_errors(query, pipeline.source.config[ElasticSource.CONFIG_OFFSET_FIELD])
        if errors:
            raise click.ClickException(errors)


def get_config_validator(p: Pipeline) -> BaseValidator:
    if p.source.type == source.TYPE_ELASTIC:
        return ElasticValidator()
    return BaseValidator()
