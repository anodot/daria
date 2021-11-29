from agent import streamsets


def check_streamsets() -> str:
    if len(streamsets.repository.get_all()) <= 0:
        return 'StreamSets is not configured, please add streamsets first'
