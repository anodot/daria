from typing import Optional
from . import db
from agent.modules import db as agent_db
from agent.pipeline import Pipeline
from .cacti import SourcesCache


def get_cacti_sources(mysql_connection_string: str, exclude_hosts: list, exclude_datasources: list) -> list:
    if exclude_hosts or exclude_datasources:
        query = _build_query(exclude_datasources, exclude_hosts)
    else:
        query = 'SELECT name, name_cache, data_source_path FROM data_template_data'
    session = db.get_session(mysql_connection_string)
    res = session.execute(query)
    session.close()
    return res


def _build_query(exclude_datasources: list, exclude_hosts: list):
    query = """
        SELECT dtd.name, dtd.name_cache, dtd.data_source_path
        FROM data_template_data dtd
        JOIN data_local dl ON dtd.local_data_id = dl.id
        JOIN host h ON h.id = dl.host_id
        WHERE 1=1
    """
    for host in exclude_hosts:
        query += f"AND h.description NOT LIKE '{host.replace('*', '%')}' "
    for data_source in exclude_datasources:
        query += f"AND dtd.name_cache NOT LIKE '{data_source.replace('*', '%')}' "
    return query


def get_cacti_source_cache(pipeline_: Pipeline) -> Optional[SourcesCache]:
    return agent_db.Session\
            .query(SourcesCache)\
            .filter(SourcesCache.pipeline_id == pipeline_.name).first()


def save_source_cache(source_cache: SourcesCache):
    if not agent_db.Session.object_session(source_cache):
        agent_db.Session.add(source_cache)
    agent_db.Session.commit()
