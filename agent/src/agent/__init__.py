from agent import destination, streamsets


def check_prerequisites() -> list:
    errors = []
    if not destination.repository.exists():
        errors.append('Destination is not configured, please create agent destination first')
    if not len(streamsets.repository.get_all()) > 0:
        errors.append('StreamSets is not configured, please add streamsets first')
    return errors
