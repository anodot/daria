from typing import Optional
from agent import source
from agent.data_extractor.cacti.cacher import CactiCache
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


class CactiCacher:
    def __init__(self, pipeline_: Pipeline):
        mysql_connection_string = pipeline_.source.config[source.CactiSource.MYSQL_CONNECTION_STRING]
        self.session = scoped_session(sessionmaker(bind=create_engine(mysql_connection_string)))
        self.pipeline = pipeline_
        self.graphs = {}
        self.hosts = {}
        self._get_graph_items()
        self._get_graph_titles()
        self._get_graph_variables()
        self._get_items_variables()
        self._get_hosts()
        self._get_item_cdef_items()

    def _get_graph_titles(self):
        res = self.session.execute(f"""
            SELECT gtg.local_graph_id, gtg.title, gl.host_id
            FROM graph_templates_graph gtg
            JOIN graph_local gl ON gtg.local_graph_id = gl.id
            WHERE local_graph_id != 0 {self._filter_by_graph_ids('gtg.local_graph_id', add_and=True)}
        """)
        for row in res:
            if row['local_graph_id'] not in self.graphs:
                continue
            self.graphs[row['local_graph_id']]['title'] = row['title']
            self.graphs[row['local_graph_id']]['host_id'] = str(row['host_id'])

    def _get_graph_variables(self):
        res = self.session.execute(f"""
            SELECT gl.id, field_name, field_value
            FROM host_snmp_cache hsc FORCE INDEX (`PRIMARY`)
            JOIN graph_local gl
            ON gl.host_id = hsc.host_id
            AND gl.snmp_index = hsc.snmp_index
            AND gl.snmp_query_id = hsc.snmp_query_id
            WHERE {self._filter_by_graph_ids('gl.id')}
        """)
        for row in res:
            local_graph_id = row['id']
            if local_graph_id not in self.graphs:
                continue
            if 'variables' not in self.graphs[local_graph_id]:
                self.graphs[local_graph_id]['variables'] = {}
            self.graphs[local_graph_id]['variables'][row['field_name']] = row['field_value']

    def _get_graph_items(self):
        # (4, 5, 6, 7 ,8) are ids of AREA, STACK, LINE1, LINE2, and LINE3 graph item types
        res = self.session.execute(f"""
            SELECT gti.id as item_id, gti.local_graph_id, dtr.data_source_name, gti.text_format as item_title, dtd.data_source_path
            FROM graph_templates_item gti
            JOIN graph_templates_graph gtg on gti.local_graph_id = gtg.local_graph_id
            JOIN data_template_rrd dtr on dtr.id = gti.task_item_id
            JOIN data_template_data dtd on dtd.local_data_id = dtr.local_data_id
            WHERE gtg.local_graph_id != 0
            AND gti.graph_type_id IN (4, 5, 6, 7 ,8)
            AND dtd.data_source_path IS NOT NULL
            {self._filter_by_graph_ids('gti.local_graph_id', add_and=True)}
        """)
        for row in res:
            local_graph_id = row['local_graph_id']
            if local_graph_id not in self.graphs:
                self.graphs[local_graph_id] = {}
            if 'items' not in self.graphs[local_graph_id]:
                self.graphs[local_graph_id]['items'] = {}
            if row['item_id'] not in self.graphs[local_graph_id]['items']:
                self.graphs[local_graph_id]['items'][row['item_id']] = {}

            self.graphs[local_graph_id]['items'][row['item_id']]['data_source_path'] = row['data_source_path']
            self.graphs[local_graph_id]['items'][row['item_id']]['data_source_name'] = row['data_source_name']
            self.graphs[local_graph_id]['items'][row['item_id']]['item_title'] = row['item_title']

    def _get_items_variables(self):
        res = self.session.execute(f"""
            SELECT gti.id AS item_id, gti.local_graph_id, hsc.field_name, hsc.field_value, hsc.host_id
            FROM graph_templates_item AS gti
                JOIN data_template_rrd AS dtr ON gti.task_item_id = dtr.id
                JOIN data_local AS dl ON dl.id = dtr.local_data_id
                JOIN host_snmp_cache hsc FORCE INDEX (`PRIMARY`)
            WHERE hsc.host_id = dl.host_id
            AND hsc.snmp_query_id = dl.snmp_query_id
            AND hsc.snmp_index = dl.snmp_index
            {self._filter_by_graph_ids('gti.local_graph_id', add_and=True)}
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

    def _get_item_cdef_items(self):
        res = self.session.execute(f"""
            SELECT gti.id as item_id, gti.local_graph_id, ci.sequence, ci.value
            FROM cdef_items ci
            JOIN graph_templates_item gti on gti.cdef_id = ci.cdef_id
            WHERE gti.cdef_id != 0
            AND gti.local_graph_id != 0
            {self._filter_by_graph_ids('gti.local_graph_id', add_and=True)}
            ORDER BY item_id, sequence
        """)
        for row in res:
            if row['local_graph_id'] not in self.graphs:
                continue
            graph = self.graphs[row['local_graph_id']]
            if row['item_id'] not in graph['items']:
                continue
            item = graph['items'][row['item_id']]
            if 'cdef_items' not in item:
                item['cdef_items'] = {}
            item['cdef_items'][row['sequence']] = row['value']

    def _filter_by_graph_ids(self, field_name, add_and=False):
        graph_ids = self.pipeline.config.get('graph_ids')
        if not graph_ids:
            return ''
        condition = 'AND ' if add_and else ''
        condition += f'{field_name} in ({",".join(graph_ids)})'
        return condition

    def get_data(self) -> dict:
        return {
            'hosts': self.hosts,
            'graphs': self.graphs,
        }
