from agent import destination, pipeline
from agent.modules import proxy
from result import Result, Ok, Err


def create(
    token: str,
    url: str,
    access_key: str = None,
    proxy_host: str = None,
    proxy_username: str = None,
    proxy_password: str = None,
    host_id: str = None,
) -> Result[destination.HttpDestination, str]:
    result = _build(destination.HttpDestination(), token, url, access_key, proxy_host, proxy_username, proxy_password, host_id)
    if not result.is_err():
        destination.repository.save(result.value)
        pipeline.manager.start_monitoring_pipeline()
    return result


def edit(
    destination_: destination.HttpDestination,
    token: str,
    url: str,
    access_key: str = None,
    proxy_host: str = None,
    proxy_username: str = None,
    proxy_password: str = None,
    host_id: str = None,
) -> Result[destination.HttpDestination, str]:
    result = _build(destination_, token, url, access_key, proxy_host, proxy_username, proxy_password, host_id)
    if not result.is_err():
        destination.repository.save(result.value)
        pipeline.manager.update_monitoring_pipeline()
    return result


def _build(
    destination_: destination.HttpDestination,
    token: str,
    url: str,
    access_key: str = None,
    proxy_host: str = None,
    proxy_username: str = None,
    proxy_password: str = None,
    host_id: str = None,
) -> Result[destination.HttpDestination, str]:
    proxy_ = proxy.Proxy(proxy_host, proxy_username, proxy_password) if proxy_host else None
    if proxy_:
        if not proxy.is_valid(proxy_):
            return Err('Proxy data is invalid')
        destination_.proxy = proxy_
    if url:
        try:
            destination.validator.is_valid_destination_url(url, destination_.proxy)
        except destination.validator.ValidationException as e:
            return Err('Destination url validation failed: ' + str(e))
        destination_.url = url
    if token:
        destination_.token = token
        if not destination.validator.is_valid_resource_url(destination_.resource_url):
            return Err('Data collection token is invalid')
    if access_key:
        if not destination.validator.is_valid_access_key(access_key, destination_.proxy, destination_.url):
            return Err('Access key is invalid')
        destination_.access_key = access_key
    if host_id:
        destination_.host_id = host_id
    return Ok(destination_)


def delete():
    pipeline.manager.stop_by_id(pipeline.MONITORING)
    pipeline.manager.delete_by_name(pipeline.MONITORING)
    destination.repository.delete()
