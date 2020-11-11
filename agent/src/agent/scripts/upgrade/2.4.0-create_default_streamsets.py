from agent import streamsets, pipeline
from agent.modules import constants, db
from agent.streamsets import StreamSets

if len(streamsets.repository.get_all()) > 0:
    print('You already have a streamsets instance in the db')
    exit(1)

streamsets.repository.save(StreamSets(
    constants.DEFAULT_STREAMSETS_URL,
    constants.DEFAULT_STREAMSETS_USERNAME,
    constants.DEFAULT_STREAMSETS_PASSWORD,
))

streamsets_ = streamsets.repository.get_all()[0]
for p in pipeline.repository.get_all():
    p.set_streamsets(streamsets_)
    pipeline.repository.save(p)

# todo this is temporary
db.session().commit()
db.session().close()
