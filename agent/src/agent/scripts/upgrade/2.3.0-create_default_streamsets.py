from agent import streamsets
from agent.modules import constants
from agent.streamsets import StreamSets

streamsets.repository.save(StreamSets(
    constants.DEFAULT_STREAMSETS_URL,
    constants.DEFAULT_STREAMSETS_USERNAME,
    constants.DEFAULT_STREAMSETS_PASSWORD,
))
