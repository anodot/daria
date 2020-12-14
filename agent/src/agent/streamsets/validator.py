import sdc_client

from agent.streamsets import StreamSets


def validate(streamsets_: StreamSets):
    try:
        sdc_client.check_connection(streamsets_)
    except sdc_client.UnauthorizedException:
        raise ValidationException('Wrong username or password provided')
    except sdc_client.ApiClientException as e:
        raise ValidationException(str(e))


class ValidationException(Exception):
    pass
