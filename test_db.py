from agent.db import Session
from agent import destination, source, pipeline

session = Session()

# s = session.query(source.Source).filter(source.Source.name == 'test_influx').first()
s = source.repository.get_by_name('test_influx')
t = 1
# s.config['configBean.initialOffset'] = 300
# session.commit()

# session.add(source.Source('source6', 'kafka', {"key1": "val1"}))
# session.add(entity.Pipeline(name='pipeline1', source_id=3, config={"key1": "val1"}))
# source = session.query(entity.Source).filter(entity.Source.name == 'source2').first()
# source = session.query(entity.Pipeline).filter(entity.Pipeline.name == 'pipeline1').first()
# session.delete(source)
# session.commit()

# res = session.query(entity.Source).filter(entity.Source.name.like('source1%')).all()

# session.add(entity.Destination(host_id='source2', access_key='', config={"key1": "val1"}))
# session.commit()
#
# session.query(entity.Destination).delete()
# session.commit()
# rea = session.query(
#         session.query(entity.Destination).exists()
#     ).scalar()

# p = pipeline.repository.get_by_name('Monitoring')

t = 1
