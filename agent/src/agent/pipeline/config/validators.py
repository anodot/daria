import click

from agent.pipeline.validators import elastic_query, jdbc_query
from agent import source


# todo don't raise ClickException here, we need ValidationException

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


# todo remove
# class SNMPValidator(BaseValidator):
#     @staticmethod
#     def validate(pipeline):
#         timezone = pipeline.config["timezone"]
#         if timezone and timezone not in pytz.all_timezones:
#             raise click.ClickException(f"Timezone `{timezone}` is invalid")


def get_config_validator(source_type: str) -> BaseValidator:
    if source_type == source.TYPE_ELASTIC:
        return ElasticValidator()
    elif source_type in [source.TYPE_MYSQL, source.TYPE_POSTGRES, source.TYPE_CLICKHOUSE]:
        return JDBCValidator()
    # elif source_type == source.TYPE_SNMP:
    #     return SNMPValidator()
    return BaseValidator()
