from typing import Optional
from agent.data_extractor.cacti.source_cacher import CactiCache
from agent.modules import db as agent_db
from agent.pipeline import Pipeline
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


def _get_session(connection_string: str):
    return scoped_session(sessionmaker(bind=create_engine(connection_string)))


def get_cache(pipeline_: Pipeline) -> Optional[CactiCache]:
    return agent_db.Session\
            .query(CactiCache)\
            .filter(CactiCache.pipeline_id == pipeline_.name).first()


def save_cacti_cache(source_cache: CactiCache):
    if not agent_db.Session.object_session(source_cache):
        agent_db.Session.add(source_cache)
    agent_db.Session.commit()


def get_variables(mysql_connection_string: str) -> dict:
    variables = {}
    res = _get_session(mysql_connection_string).execute("""
        SELECT DISTINCT gti.id, gti.local_graph_id, hsc.field_name, hsc.field_value, hsc.host_id
        FROM graph_templates_item AS gti
            JOIN data_template_rrd AS dtr ON gti.task_item_id = dtr.id
            JOIN data_local AS dl ON dl.id = dtr.local_data_id
            JOIN host_snmp_cache hsc
        WHERE hsc.host_id = dl.host_id
        AND hsc.snmp_query_id = dl.snmp_query_id
        AND hsc.snmp_index = dl.snmp_index
    """)
    for row in res:
        item_id = row['id']
        local_graph_id = row['local_graph_id']
        if local_graph_id not in variables:
            variables[local_graph_id] = {'host_id': row['host_id']}
        if item_id not in variables[local_graph_id]:
            variables[local_graph_id][item_id] = {}

        if row['field_name'] in variables[local_graph_id] and row['field_value'] != variables[local_graph_id][row['field_name']]:
            # завтра пробежаться дебаггером, если попадем сюда - то мы затираем переменные для разных айтемов
            t = 1

        variables[local_graph_id][item_id][row['field_name']] = row['field_value']
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


def get_graph_items(mysql_connection_string: str) -> dict:
    graph_items = {}
    res = _get_session(mysql_connection_string).execute("""
        SELECT gti.id as item_id, local_graph_id, dtr.data_source_name
        FROM graph_templates_item gti
        JOIN graph_templates_graph on gti.local_graph_id = gtg.local_graph_id
        JOIN data_template_rrd dtr on dtr.id = gti.task_item_id
    """)
    for row in res:
        local_graph_id = row['local_graph_id']
        if local_graph_id not in graph_items:
            graph_items[local_graph_id] = {}
        graph_items[local_graph_id]['item_id'] = row['item_id']
        graph_items[local_graph_id]['data_source_name'] = row['data_source_name']
    return graph_items


def get_sources(mysql_connection_string: str) -> dict:
    data_sources = {}
    res = _get_session(mysql_connection_string).execute("""
        SELECT DISTINCT gti.local_graph_id, dtd.data_source_path
        FROM graph_templates_item AS gti
        JOIN data_template_rrd AS dtr ON gti.task_item_id = dtr.id
        JOIN data_template_data dtd on dtd.local_data_id = dtr.local_data_id
        WHERE local_graph_id != 0
        AND data_source_path IS NOT NULL
    """)
    for row in res:
        data_sources[row['local_graph_id']] = row['data_source_path']
    return data_sources


# =============================================================================

class S:
    def __init__(self, mysql_connection_string: str):
        self.session = scoped_session(sessionmaker(bind=create_engine(mysql_connection_string)))
        self.graphs = {}
        self.hosts = {}
        self._get_sources()
        self._get_graph_titles()
        self._get_graph_variables()
        self._get_graph_items()
        self._get_variables()
        self._get_hosts()

    def _get_sources(self):
        res = self.session.execute("""
            SELECT gti.id as item_id, gti.local_graph_id, dtd.data_source_path
            FROM graph_templates_item AS gti
            JOIN data_template_rrd AS dtr ON gti.task_item_id = dtr.id
            JOIN data_template_data dtd on dtd.local_data_id = dtr.local_data_id
            WHERE local_graph_id != 0
            AND data_source_path IS NOT NULL;
        """)
        for row in res:
            local_graph_id = row['local_graph_id']
            if local_graph_id not in self.graphs:
                self.graphs[local_graph_id] = {}
            if 'items' not in self.graphs[local_graph_id]:
                self.graphs[local_graph_id]['items'] = {}
            self.graphs[local_graph_id]['items'][row['item_id']] = {'data_source_path': row['data_source_path']}

    def _get_graph_titles(self):
        res = self.session.execute("""
            SELECT gtg.local_graph_id, gtg.title, gl.host_id
            FROM graph_templates_graph gtg
            JOIN graph_local gl ON gtg.local_graph_id = gl.id
            WHERE local_graph_id != 0
        """)
        for row in res:
            if row['local_graph_id'] not in self.graphs:
                continue
            self.graphs[row['local_graph_id']]['title'] = row['title']
            self.graphs[row['local_graph_id']]['host_id'] = str(row['host_id'])

    def _get_graph_variables(self):
        res = self.session.execute("""
            select gl.id, field_name, field_value
            from host_snmp_cache hsc
            join graph_local gl
            on gl.host_id = hsc.host_id
            and gl.snmp_index = hsc.snmp_index
            and gl.snmp_query_id = hsc.snmp_query_id
        """)
        for row in res:
            local_graph_id = row['id']
            if local_graph_id not in self.graphs:
                continue
            if 'variables' not in self.graphs[local_graph_id]:
                self.graphs[local_graph_id]['variables'] = {}
            self.graphs[local_graph_id]['variables'][row['field_name']] = row['field_value']

    def _get_graph_items(self):
        res = self.session.execute("""
            SELECT gti.id as item_id, gti.local_graph_id, dtr.data_source_name, gti.text_format as item_title
            FROM graph_templates_item gti
            JOIN graph_templates_graph gtg on gti.local_graph_id = gtg.local_graph_id
            JOIN data_template_rrd dtr on dtr.id = gti.task_item_id
            WHERE gtg.local_graph_id != 0
        """)
        for row in res:
            local_graph_id = row['local_graph_id']
            if local_graph_id not in self.graphs:
                continue
            if 'items' not in self.graphs[local_graph_id]:
                self.graphs[local_graph_id]['items'] = []
            if row['item_id'] not in self.graphs[local_graph_id]['items']:
                continue

            self.graphs[local_graph_id]['items'][row['item_id']]['data_source_name'] = row['data_source_name']
            self.graphs[local_graph_id]['items'][row['item_id']]['item_title'] = row['item_title']

    def _get_variables(self):
        res = self.session.execute("""
            SELECT gti.id AS item_id, gti.local_graph_id, hsc.field_name, hsc.field_value, hsc.host_id
            FROM graph_templates_item AS gti
                JOIN data_template_rrd AS dtr ON gti.task_item_id = dtr.id
                JOIN data_local AS dl ON dl.id = dtr.local_data_id
                JOIN host_snmp_cache hsc FORCE INDEX (`PRIMARY`)
            WHERE hsc.host_id = dl.host_id
            AND hsc.snmp_query_id = dl.snmp_query_id
            AND hsc.snmp_index = dl.snmp_index
        """)
        for row in res:
            local_graph_id = row['local_graph_id']
            item_id = row['item_id']
            if local_graph_id not in self.graphs:
                continue
            if item_id not in self.graphs[local_graph_id]['items']:
                continue
            if 'variables' not in self.graphs[local_graph_id]['items'][item_id]:
                self.graphs[local_graph_id]['items'][item_id]['variables'] = {}

            self.graphs[local_graph_id]['items'][item_id]['host_id'] = str(row['host_id'])
            self.graphs[local_graph_id]['items'][item_id]['variables'][row['field_name']] = row['field_value']

    def _get_hosts(self):
        res = self.session.execute("""
            SELECT id, description, hostname, snmp_community, snmp_version, snmp_username, snmp_password, snmp_auth_protocol,
             snmp_priv_passphrase, snmp_context, snmp_port, snmp_timeout, ping_retries, max_oids
            FROM host
        """)
        for row in res:
            self.hosts[row['id']] = dict(row)

    def get_data(self) -> dict:
        return {
            'hosts': self.hosts,
            'graphs': self.graphs,
        }
