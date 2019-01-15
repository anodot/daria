import config
import json
import os
import time

from logger import get_logger
from streamsets_api_client import StreamSetsApiClient


logger = get_logger(__name__)
api_client = StreamSetsApiClient(config.streamsets_username, config.streamsets_password)
pipeline = api_client.create_pipeline('test impressions')

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                       'pipelines/{source_name}.json'.format(**{'source_name': config.pipeline_config['source_name']})),
          'r') as f:
    example_pipeline = json.load(f)
    example_pipeline['pipelineConfig']['uuid'] = pipeline['uuid']
    example_pipeline['pipelineConfig']['title'] = pipeline['title']

    # update source configs
    for conf in example_pipeline['pipelineConfig']['stages'][0]['configuration']:
        if conf['name'] in config.pipeline_config['source_config']:
            conf['value'] = config.pipeline_config['source_config'][conf['name']]

    for stage in example_pipeline['pipelineConfig']['stages']:
        # update adding properties field stage
        if stage['instanceName'] == 'ExpressionEvaluator_01':
            for conf in stage['configuration']:
                if conf['name'] == 'expressionProcessorConfigs':
                    conf['value'][1]['expression'] = config.pipeline_config['measurement_name']

        # update renamer map
        if stage['instanceName'] == 'FieldRenamer_01':
            for conf in stage['configuration']:
                if conf['name'] == 'renameMapping':
                    rename_mapping = [
                        {'fromFieldExpression': '/' + config.pipeline_config['value_field_name'],
                         'toFieldExpression': '/value'}
                    ]
                    if config.pipeline_config['timestamp_field_name'] != 'timestamp':
                        rename_mapping.append(
                            {'fromFieldExpression': '/' + config.pipeline_config['timestamp_field_name'],
                             'toFieldExpression': '/timestamp'})
                    for dim in config.pipeline_config['dimensions']:
                        rename_mapping.append(
                            {'fromFieldExpression': '/' + dim, 'toFieldExpression': '/properties/' + dim})
                    conf['value'] = rename_mapping

        # update http client
        if stage['instanceName'] == 'HTTPClient_01':
            for conf in stage['configuration']:
                if conf['name'] == 'conf.resourceUrl':
                    conf['value'] = config.pipeline_config['destination_url']

    api_client.update_pipeline(pipeline['pipelineId'], example_pipeline['pipelineConfig'])

    pipeline_rules = api_client.get_pipeline_rules(pipeline['pipelineId'])
    example_pipeline['pipelineRules']['uuid'] = pipeline_rules['uuid']
    api_client.update_pipeline_rules(pipeline['pipelineId'], example_pipeline['pipelineRules'])

api_client.start_pipeline(pipeline['pipelineId'])

time.sleep(13)
api_client.stop_pipeline(pipeline['pipelineId'])
