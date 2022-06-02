from agent import source
from agent.source import sensitive_data


def test_masking_supports_all_sources():
    dummy_config = {
        'bla': 'bla-bla',
        'config': {
            'bla': 'bla-bla',
        }
    }
    for source_type in source.types.keys():
        dummy_config['type'] = source_type
        _ = sensitive_data.mask(dummy_config)


def test_mask_sensitive_data():
    c = {
        'type': source.TYPE_PROMETHEUS,
        'config': {
            'bla': 'bla-bla',
            'username': 'user',
            'another': {
                'password': 'pass',
            }
        }
    }
    er = {
        'type': source.TYPE_PROMETHEUS,
        'config': {
            'bla': 'bla-bla',
            'username': source.sensitive_data.MASK,
            'another': {
                'password': source.sensitive_data.MASK,
            }
        }
    }
    assert source.sensitive_data.mask(c) == er
