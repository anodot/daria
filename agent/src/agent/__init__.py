from agent import destination, streamsets, source


def check_prerequisites() -> list:
    errors = []
    if not destination.repository.exists():
        errors.append('Destination is not configured, please create agent destination first')
    if e := _check_streamsets():
        errors.append(e)
    return errors


def check_raw_prerequisites() -> list:
    errors = []
    if e := _check_streamsets():
        errors.append(e)
    return errors


def _check_streamsets() -> str:
    if not len(streamsets.repository.get_all()) > 0:
        return 'StreamSets is not configured, please add streamsets first'
