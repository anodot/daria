from . import db
from agent.source import Source, source


def get_cacti_sources(source_: Source, exclude_hosts: list, exclude_datasources: list) -> dict:
    # todo
    source_.config[source.CactiSource.MYSQL_CONNECTION_STRING] = 'mysql://root@127.0.0.1:3308/cacti'
    if exclude_hosts or exclude_datasources:
        query = _build_query(exclude_datasources, exclude_hosts)
    else:
        query = 'SELECT name, name_cache, data_source_path FROM data_template_data'
    session = db.get_session(source_.get_connection_string())
    res = session.execute(query)
    session.close()
    return res


def _build_query(exclude_datasources: str, exclude_hosts: str):
    query = """
        SELECT dtd.name, dtd.name_cache, dtd.data_source_path
        FROM data_template_data dtd
        JOIN data_local dl ON dtd.local_data_id = dl.id
        WHERE 1=1
    """
    for host in exclude_hosts:
        query += f"AND h.description NOT LIKE '{host}' "
    for data_source in exclude_datasources:
        query += f"AND dtd.name_cache NOT LIKE '{data_source}' "
    return query
