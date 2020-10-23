from agent.modules import streamsets, constants
from agent.modules.streamsets import StreamSets

streamsets.repository.save(StreamSets(
    constants.DEFAULT_STREAMSETS_URL,
    constants.DEFAULT_STREAMSETS_USERNAME,
    constants.DEFAULT_STREAMSETS_PASSWORD,
))
