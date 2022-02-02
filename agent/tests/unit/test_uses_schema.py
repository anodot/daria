from agent import source
from agent.pipeline.json_builder import json_builder


class Object(object):
    pass


def test_uses_schema():
    pipeline_ = Object()
    pipeline_.source = source.PromQLSource('name', 'victoria', {})

    config = {'dimensions': ['adf'], 'values': {'value': 'gauge'}, 'uses_schema': True}
    assert json_builder._uses_schema(pipeline_, config) is True
    config = {'dimensions': ['adf'], 'values': {'value': 'gauge'}, 'uses_schema': False}
    assert json_builder._uses_schema(pipeline_, config) is False
    config = {'dimensions': ['adf'], 'values': {'value': 'gauge'}}
    assert json_builder._uses_schema(pipeline_, config) is True
    pipeline_.source = source.JDBCSource('name', 'mysql', {})
    assert json_builder._uses_schema(pipeline_, config) is True


def test_uses_schema_dimensions_exception():
    try:
        pipeline_ = Object()
        pipeline_.source = source.PromQLSource('name', 'victoria', {})
        config = {'dimensions': [], 'values': {'value': 'gauge'}, 'uses_schema': True}
        json_builder._uses_schema(pipeline_, config)
    except json_builder.ConfigurationException:
        return
    assert False


def test_uses_schema_values_exception():
    try:
        pipeline_ = Object()
        pipeline_.source = source.PromQLSource('name', 'victoria', {})
        config = {'dimensions': ['dim'], 'uses_schema': True}
        json_builder._uses_schema(pipeline_, config)
    except json_builder.ConfigurationException:
        return
    assert False
