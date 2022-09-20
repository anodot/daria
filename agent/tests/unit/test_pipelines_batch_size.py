import json
import os

from agent.modules import constants


def test_pipelines_batch_size():
    _check_dir(os.path.join(constants.ROOT_DIR, 'pipeline/config/base_pipelines/'))


def _check_dir(dir_path: str, batch_size: int = 1000):
    for path in os.listdir(dir_path):
        full_path = os.path.join(dir_path, path)
        if os.path.isdir(full_path):
            if path.endswith('events'):
                _check_dir(full_path, 1)
            else:
                _check_dir(full_path)
        else:
            _check_file(full_path, batch_size)


def _check_file(file_path, batch_size):
    with open(file_path, 'r') as f:
        for stage in json.load(f)['pipelineConfig']['stages']:
            for configuration in stage['configuration']:
                if configuration['name'] == 'scriptConf.batchSize':
                    assert configuration['value'] == batch_size
                    print(f'Checked `{file_path}` batch size')
                    return
                elif configuration['name'] == 'conf.batchSize':
                    assert configuration['value'] == batch_size
                    print(f'Checked `{file_path}` batch size')
                    return
