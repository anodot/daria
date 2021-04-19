from typing import Optional
from agent.data_extractor.cacti.source_cacher import CactiCache
from agent.modules import db as agent_db
from agent.pipeline import Pipeline
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


def _get_session(connection_string: str):
    return scoped_session(sessionmaker(bind=create_engine(connection_string)))


def get_cacti_sources(mysql_connection_string: str, exclude_hosts: list, exclude_datasources: list) -> list:
    if exclude_hosts or exclude_datasources:
        query = _build_query(exclude_datasources, exclude_hosts)
    else:
        query = """
            SELECT dtd.name, dtd.name_cache, dtd.data_source_path, h.description, h.hostname
            FROM data_template_data dtd
            JOIN data_local dl ON dtd.local_data_id = dl.id
            JOIN host h ON h.id = dl.host_id
        """
    res = _get_session(mysql_connection_string).execute(query)
    return res


def _build_query(exclude_datasources: list, exclude_hosts: list):
    query = """
        SELECT dtd.name, dtd.name_cache, dtd.data_source_path, h.description, h.hostname
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


def get_cache(pipeline_: Pipeline) -> Optional[CactiCache]:
    return agent_db.Session\
            .query(CactiCache)\
            .filter(CactiCache.pipeline_id == pipeline_.name).first()


def save_source_cache(source_cache: CactiCache):
    if not agent_db.Session.object_session(source_cache):
        agent_db.Session.add(source_cache)
    agent_db.Session.commit()


def get_variables(mysql_connection_string: str) -> dict:
    variables = {}
    res = _get_session(mysql_connection_string).execute("""
        SELECT DISTINCT gti.local_graph_id, hsc.field_name, hsc.field_value, hsc.host_id
        FROM graph_templates_item AS gti
            JOIN data_template_rrd AS dtr ON gti.task_item_id = dtr.id
            JOIN data_local AS dl ON dl.id = dtr.local_data_id
            JOIN host_snmp_cache hsc
        WHERE hsc.host_id = dl.host_id
        AND hsc.snmp_query_id = dl.snmp_query_id
        AND hsc.snmp_index = dl.snmp_index
    """)
    for row in res:
        local_graph_id = row['local_graph_id']
        if local_graph_id not in variables:
            variables[local_graph_id] = {'host_id': row['host_id']}

        variables[local_graph_id][row['field_name']] = row['field_value']
    return variables


def get_hosts(mysql_connection_string: str) -> dict:
    hosts = {}
    res = _get_session(mysql_connection_string).execute("""
        SELECT description, hostname, snmp_community, snmp_version, snmp_username, snmp_password, snmp_auth_protocol,
         snmp_priv_passphrase, snmp_context, snmp_port, snmp_timeout, ping_retries, max_oids, id
        FROM host
    """)
    for row in res:
        hosts[row['id']] = dict(row)
    return hosts


def get_graphs(mysql_connection_string: str) -> dict:
    graphs = {}
    res = _get_session(mysql_connection_string).execute("""
        SELECT local_graph_id, title FROM graph_templates_graph
    """)
    for row in res:
        graphs[row['local_graph_id']] = row['title']
    return graphs


def get_sources(mysql_connection_string: str) -> dict:
    data_sources = {}
    res = _get_session(mysql_connection_string).execute("""
        SELECT DISTINCT gti.local_graph_id, dtd.data_source_path
        FROM graph_templates_item AS gti
        JOIN data_template_rrd AS dtr ON gti.task_item_id = dtr.id
        JOIN data_template_data dtd on dtd.local_data_id = dtr.local_data_id
    """)
    for row in res:
        data_sources[row['local_graph_id']] = row['data_source_path']
    return data_sources
