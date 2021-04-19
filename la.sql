select graph_local.host_id,
       graph_local.snmp_query_id,
       graph_local.snmp_index,
       graph_templates_graph.local_graph_id,
       graph_templates_graph.title
from (graph_templates_graph,graph_local)
where graph_templates_graph.local_graph_id = graph_local.id
  and graph_local.id = 13882;


SELECT DISTINCT local_data_id
FROM data_template_rrd
         INNER JOIN graph_templates_item ON data_template_rrd.id = graph_templates_item.task_item_id
WHERE local_graph_id = 13882;


SELECT id
FROM data_template_data
WHERE local_data_id IN (13744);


SELECT dif.data_name, did.value
FROM data_input_fields AS dif
         INNER JOIN data_input_data AS did ON dif.id = did.data_input_field_id
WHERE data_template_data_id = 13866
  AND input_output = 'in';


select field_name, field_value
from host_snmp_cache
where host_id = 1008
  and snmp_query_id = 1
  and snmp_index = '9';


select graph_local.host_id,
       graph_local.snmp_query_id,
       graph_local.snmp_index,
       graph_templates_graph.local_graph_id,
       graph_templates_graph.title
from (graph_templates_graph,graph_local)
where graph_templates_graph.local_graph_id = graph_local.id
  and graph_local.id = 13882;


SELECT DISTINCT local_data_id
FROM data_template_rrd
         INNER JOIN graph_templates_item ON data_template_rrd.id = graph_templates_item.task_item_id
WHERE local_graph_id = 13882;


SELECT id
FROM data_template_data
WHERE local_data_id IN (13744);
SELECT dif.data_name, did.value
FROM data_input_fields AS dif
         INNER JOIN data_input_data AS did ON dif.id = did.data_input_field_id
WHERE data_template_data_id = 13866
  AND input_output = 'in';


select field_name, field_value
from host_snmp_cache
where host_id = 1008
  and snmp_query_id = 1
  and snmp_index = '9'