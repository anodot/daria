import json
import os

from agent.modules import constants


def test_pipelines_batch_size():
    _check_dir(os.path.join(constants.ROOT_DIR, 'pipeline/config/base_pipelines/'))


def _check_dir(dir_path):
    for path in os.listdir(dir_path):
        path = os.path.join(dir_path, path)
        if os.path.isdir(path):
            _check_dir(path)
        else:
            _check_file(path)


def _check_file(file_path):
    with open(file_path, 'r') as f:
        for stage in json.load(f)['pipelineConfig']['stages']:
            for configuration in stage['configuration']:
                if configuration['name'] == 'scriptConf.batchSize':
                    assert configuration['value'] >= 1000
                    print(f'Checked `{file_path}` batch size')
                    return
