from agent import source
from agent.source import sensitive_data


def test_timestamp_validation():
    dummy_config = {
        'bla': 'bla-bla',
        'config': {
            'bla': 'bla-bla',
        }
    }
    for source_type in source.types.keys():
        dummy_config['type'] = source_type
        sensitive_data.mask(dummy_config)
