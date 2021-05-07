from agent import pipeline
from sqlalchemy.orm.attributes import flag_modified

for pipeline_ in pipeline.repository.get_all():
    is_modified = False
    if pipeline_.config.get('count_records') and type(pipeline_.config['count_records']) is not bool:
        pipeline_.config['count_records'] = bool(pipeline_.config['count_records'])
        is_modified = True

    if pipeline_.config.get('uses_schema') is None:
        pipeline_.config['uses_schema'] = False
        is_modified = True

    if pipeline_.config.get('pipeline_id') is None:
        pipeline_.config['pipeline_id'] = pipeline_.name
        is_modified = True

    if not is_modified:
        print(f'Skipping pipeline {pipeline_.name}')
        continue

    flag_modified(pipeline_, 'config')
    pipeline.repository.save(pipeline_)
    print(f'Updated pipeline {pipeline_.name}')
