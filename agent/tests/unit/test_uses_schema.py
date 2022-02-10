from agent import source
from agent.pipeline.json_builder import json_builder


class Object(object):
    pass


def test_uses_schema():
    pipeline_ = Object()
    pipeline_.source = source.PromQLSource('name', 'victoria', {})
    chooser = json_builder._PromQLSchemaChooser()

    config = {'dimensions': ['adf'], 'values': {'value': 'gauge'}, 'uses_schema': True}
    assert chooser.choose(pipeline_, config) is True
    config = {'dimensions': ['adf'], 'values': {'value': 'gauge'}, 'uses_schema': False}
    assert chooser.choose(pipeline_, config) is False
    config = {'dimensions': ['adf'], 'values': {'value': 'gauge'}}
    assert chooser.choose(pipeline_, config) is True
    pipeline_.source = source.JDBCSource('name', 'mysql', {})
    assert chooser.choose(pipeline_, config) is True


def test_uses_schema_dimensions_exception():
    try:
        pipeline_ = Object()
        pipeline_.source = source.PromQLSource('name', 'victoria', {})
        config = {'dimensions': [], 'values': {'value': 'gauge'}, 'uses_schema': True}
        chooser = json_builder._PromQLSchemaChooser()

        chooser.choose(pipeline_, config)
    except json_builder.ConfigurationException:
        return
    assert False


def test_uses_schema_values_exception():
    try:
        pipeline_ = Object()
        pipeline_.source = source.PromQLSource('name', 'victoria', {})
        config = {'dimensions': ['dim'], 'uses_schema': True}
        chooser = json_builder._PromQLSchemaChooser()

        chooser.choose(pipeline_, config)
    except json_builder.ConfigurationException:
        return
    assert False
