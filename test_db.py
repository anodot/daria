from agent.db import Session, entity

session = Session()

# session.add(entity.Source(name='source2', type='kafka', config={"key1": "val1"}))
# session.add(entity.Pipeline(name='pipeline1', source_id=3, config={"key1": "val1"}))
# source = session.query(entity.Source).filter(entity.Source.name == 'source2').first()
# source = session.query(entity.Pipeline).filter(entity.Pipeline.name == 'pipeline1').first()
# session.delete(source)
# session.commit()

res = session.query(entity.Source).filter(entity.Source.name.like('source1%')).all()

t = 1
