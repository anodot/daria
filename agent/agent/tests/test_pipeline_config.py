import pytest

from ..pipeline_config_handler import PipelineConfigHandler


@pytest.fixture()
def pipeline_config_handler():
    client_config = {
        'name': 'test',
        'source_name': 'mongo',
        'source': 'mongo',
        'source_config': {
            'configBean.mongoConfig.username': 'username',
            'configBean.mongoConfig.password': 'password',
        },
        'measurement_name': 'impressions',
        'value_field_name': 'Impressions',
        'timestamp': {'name': 'timestamp_t', 'type': 'unix'},
        'dimensions': {'required': ['Country', 'ver']},
        'destination_url': 'http://anodot.com'
    }
    return PipelineConfigHandler(client_config)


def test_update_source_config(pipeline_config_handler):
    pipeline_config_handler.update_source_configs()
    compared = []
    for conf in pipeline_config_handler.config['stages'][0]['configuration']:
        if conf['name'] == 'configBean.mongoConfig.username':
            compared.append(conf['value'] == 'username')
        if conf['name'] == 'configBean.mongoConfig.password':
            compared.append(conf['value'] == 'password')
    assert len(compared) == 2 and all(compared)


def test_update_http_client(pipeline_config_handler):
    pipeline_config_handler.update_http_client()
    stages_count = len(pipeline_config_handler.config['stages'])
    for conf in pipeline_config_handler.config['stages'][stages_count - 1]['configuration']:
        if conf['name'] == 'conf.resourceUrl':
            assert conf['value'] == 'http://anodot.com'
            return
    pytest.fail('No config found')


def test_update_measurement_name(pipeline_config_handler):
    for stage in pipeline_config_handler.config['stages']:
        if stage['instanceName'] != 'ExpressionEvaluator_01':
            continue

        pipeline_config_handler.update_measurement_name(stage)
        for conf in stage['configuration']:
            if conf['name'] != 'expressionProcessorConfigs':
                continue
            assert conf['value'][1]['expression'] == 'impressions'
            return
    pytest.fail('No config found')


def test_override_base_rules(pipeline_config_handler):
    res = pipeline_config_handler.override_base_rules('12345')
    assert res['uuid'] == '12345'


def test_override_base_config(pipeline_config_handler, mocker):
    mocker.patch.object(pipeline_config_handler, 'update_source_configs')
    mocker.patch.object(pipeline_config_handler, 'update_measurement_name')
    mocker.patch.object(pipeline_config_handler, 'rename_fields_for_anodot_protocol')
    mocker.patch.object(pipeline_config_handler, 'update_http_client')
    mocker.patch.object(pipeline_config_handler, 'convert_timestamp_to_unix')

    res = pipeline_config_handler.override_base_config('12345', 'title test')

    assert res['uuid'] == '12345' and res['title'] == 'title test'
    pipeline_config_handler.update_source_configs.assert_called_once()
    pipeline_config_handler.update_measurement_name.assert_called_once()
    pipeline_config_handler.rename_fields_for_anodot_protocol.assert_called_once()
    pipeline_config_handler.update_http_client.assert_called_once()
    pipeline_config_handler.convert_timestamp_to_unix.assert_called_once()

