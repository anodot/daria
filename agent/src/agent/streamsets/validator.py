from agent import streamsets
from agent.streamsets import StreamSets


def validate(streamsets_: StreamSets):
    try:
        streamsets.StreamSetsApiClient(streamsets_).get_pipelines()
    except streamsets.UnauthorizedException:
        raise ValidationException('Wrong username or password provided')
    except streamsets.ApiClientException as e:
        raise ValidationException(str(e))


class ValidationException(Exception):
    pass
