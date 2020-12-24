from agent import destination, streamsets


def check_prerequisites() -> list:
    errors = []
    if not destination.repository.exists():
        errors.append('Destination is not configured, run "agent destination" to create one')
    if not len(streamsets.repository.get_all()) > 0:
        errors.append('StreamSets is not configured, run "agent streamsets add" to create one')
    return errors
