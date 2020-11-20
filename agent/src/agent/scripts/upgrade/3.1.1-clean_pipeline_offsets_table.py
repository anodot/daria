from agent import pipeline
from agent.modules import db

for offset in pipeline.repository.get_all_offsets():
    pipeline.repository.delete_offset(offset)

# todo this is temporary
db.session().commit()
db.session().close()
