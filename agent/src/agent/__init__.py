from agent import destination, streamsets, source, pipeline


def check_raw_prerequisites() -> list:
    errors = []
    if e := check_streamsets():
        errors.append(e)
    return errors


def check_streamsets() -> str:
    if not len(streamsets.repository.get_all()) > 0:
        return 'StreamSets is not configured, please add streamsets first'
