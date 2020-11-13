import requests
from agent import streamsets
from agent.streamsets import StreamSets


def validate(streamsets_: StreamSets):
    try:
        streamsets.StreamSetsApiClient(streamsets_).get_pipelines()
    except streamsets.UnauthorizedException:
        raise ValidationException('Wrong username or password provided')
    except streamsets.ApiClientException as e:
        raise ValidationException(str(e))


def validate_agent_external_url(url: str):
    try:
        url += '/version'
        res = requests.get(url)
        res.raise_for_status()
    except requests.exceptions.HTTPError:
        raise ValidationException(f'{url} returned {res.status_code} status code')
    except Exception as e:
        raise ValidationException(f'ERROR: {str(e)}')


class ValidationException(Exception):
    pass
