CREATE DATABASE cacti;
USE cacti;

DROP TABLE IF EXISTS `data_local`;
CREATE TABLE `data_local` (
  `id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `data_template_id` mediumint unsigned NOT NULL DEFAULT '0',
  `host_id` mediumint unsigned NOT NULL DEFAULT '0',
  `snmp_query_id` mediumint NOT NULL DEFAULT '0',
  `snmp_index` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `data_template_id` (`data_template_id`),
  KEY `snmp_query_id` (`snmp_query_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

LOCK TABLES `data_local` WRITE;
INSERT INTO `data_local` VALUES
(13744,41,1008,1,'9'),
(13745,41,1009,1,'9'),
(13746,41,1010,1,'9');
UNLOCK TABLES;

DROP TABLE IF EXISTS `data_template_data`;
CREATE TABLE `data_template_data` (
  `id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `local_data_template_data_id` mediumint unsigned NOT NULL DEFAULT '0',
  `local_data_id` mediumint unsigned NOT NULL DEFAULT '0',
  `data_template_id` mediumint unsigned NOT NULL DEFAULT '0',
  `data_input_id` mediumint unsigned NOT NULL DEFAULT '0',
  `t_name` char(2) DEFAULT NULL,
  `name` varchar(250) NOT NULL DEFAULT '',
  `name_cache` varchar(255) NOT NULL DEFAULT '',
  `data_source_path` varchar(255) DEFAULT NULL,
  `t_active` char(2) DEFAULT NULL,
  `active` char(2) DEFAULT NULL,
  `t_rrd_step` char(2) DEFAULT NULL,
  `rrd_step` mediumint unsigned NOT NULL DEFAULT '0',
  `t_rra_id` char(2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `local_data_id` (`local_data_id`),
  KEY `data_template_id` (`data_template_id`),
  KEY `data_input_id` (`data_input_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

LOCK TABLES `data_template_data` WRITE;
INSERT INTO `data_template_data` VALUES
(13866,41,13744,41,2,NULL,'|host_description| - Traffic - |query_ifName| |query_ifAlias|','390257-some_host - Traffic - Gi0/4 ENoB-Id','<path_rra>/cacti.rrd',NULL,'on',NULL,300,NULL),
(13867,41,13745,41,2,NULL,'|host_description| - Traffic - |query_ifName| |query_ifAlias|','390257-some_host - Traffic - Gi0/4 ENoB-Id','<path_rra>/cacti.rrd',NULL,'on',NULL,300,NULL),
(13868,41,13746,41,2,NULL,'|host_description| - Traffic - |query_ifName| |query_ifAlias|','390257-some_host mee too','<path_rra>/cacti.rrd',NULL,'on',NULL,300,NULL);
UNLOCK TABLES;

SET SQL_MODE='ALLOW_INVALID_DATES';
DROP TABLE IF EXISTS `host`;
CREATE TABLE `host` (
  `id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `host_template_id` mediumint unsigned NOT NULL DEFAULT '0',
  `description` varchar(150) NOT NULL DEFAULT '',
  `hostname` varchar(250) DEFAULT NULL,
  `notes` text,
  `snmp_community` varchar(100) DEFAULT NULL,
  `snmp_version` tinyint unsigned NOT NULL DEFAULT '1',
  `snmp_username` varchar(50) DEFAULT NULL,
  `snmp_password` varchar(50) DEFAULT NULL,
  `snmp_auth_protocol` char(5) DEFAULT '',
  `snmp_priv_passphrase` varchar(200) DEFAULT '',
  `snmp_priv_protocol` char(6) DEFAULT '',
  `snmp_context` varchar(64) DEFAULT '',
  `snmp_port` mediumint unsigned NOT NULL DEFAULT '161',
  `snmp_timeout` mediumint unsigned NOT NULL DEFAULT '500',
  `availability_method` smallint unsigned NOT NULL DEFAULT '1',
  `ping_method` smallint unsigned DEFAULT '0',
  `ping_port` int unsigned DEFAULT '0',
  `ping_timeout` int unsigned DEFAULT '500',
  `ping_retries` int unsigned DEFAULT '2',
  `max_oids` int unsigned DEFAULT '10',
  `device_threads` tinyint unsigned NOT NULL DEFAULT '1',
  `disabled` char(2) DEFAULT NULL,
  `manage` char(3) NOT NULL DEFAULT '',
  `thold_send_email` int NOT NULL DEFAULT '1',
  `thold_host_email` int NOT NULL,
  `monitor` char(3) NOT NULL DEFAULT 'on',
  `monitor_text` text NOT NULL,
  `status` tinyint NOT NULL DEFAULT '0',
  `status_event_count` mediumint unsigned NOT NULL DEFAULT '0',
  `status_fail_date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `status_rec_date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `status_last_error` varchar(255) DEFAULT '',
  `min_time` decimal(10,5) DEFAULT '9.99999',
  `max_time` decimal(10,5) DEFAULT '0.00000',
  `cur_time` decimal(10,5) DEFAULT '0.00000',
  `avg_time` decimal(10,5) DEFAULT '0.00000',
  `total_polls` int unsigned DEFAULT '0',
  `failed_polls` int unsigned DEFAULT '0',
  `availability` decimal(8,5) NOT NULL DEFAULT '100.00000',
  `rdistance` decimal(10,6) NOT NULL DEFAULT '0.000000',
  `groupnum` int NOT NULL DEFAULT '0',
  `stop` int NOT NULL DEFAULT '360',
  `start` int NOT NULL DEFAULT '0',
  `GPScoverage` varchar(3) NOT NULL DEFAULT 'on',
  `longitude` decimal(13,10) NOT NULL DEFAULT '0.0000000000',
  `latitude` decimal(13,10) NOT NULL DEFAULT '0.0000000000',
  PRIMARY KEY (`id`),
  KEY `disabled` (`disabled`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

LOCK TABLES `host` WRITE;
INSERT INTO `host` VALUES
(1008,5,'390257-some_host','192.168.0.1','','val',2,'','','','','','',161,500,2,1,23,400,3,10,1,'','',1,0,'on','',3,0,'0000-00-00 00:00:00','0000-00-00 00:00:00','Host did not respond to SNMP',1.07550,1519.15000,8.84000,7.28090,124425,150,99.87945,0.000000,0,0,0,'on',0.0000000000,0.0000000000),
(1009,5,'bla_exclude_me_bla 10-32o5','192.168.0.1','','val',2,'','','','','','',161,500,2,1,23,400,3,10,1,'','',1,0,'on','',3,0,'0000-00-00 00:00:00','0000-00-00 00:00:00','Host did not respond to SNMP',1.07550,1519.15000,8.84000,7.28090,124425,150,99.87945,0.000000,0,0,0,'on',0.0000000000,0.0000000000),
(1010,5,'390257-some_host','192.168.0.1','','val',2,'','','','','','',161,500,2,1,23,400,3,10,1,'','',1,0,'on','',3,0,'0000-00-00 00:00:00','0000-00-00 00:00:00','Host did not respond to SNMP',1.07550,1519.15000,8.84000,7.28090,124425,150,99.87945,0.000000,0,0,0,'on',0.0000000000,0.0000000000);
UNLOCK TABLES;

CREATE TABLE `graph_templates_item` (
  `id` int(12) unsigned NOT NULL AUTO_INCREMENT,
  `hash` varchar(32) NOT NULL DEFAULT '',
  `local_graph_template_item_id` int(12) unsigned NOT NULL DEFAULT '0',
  `local_graph_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `graph_template_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `task_item_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `color_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `alpha` char(2) DEFAULT 'FF',
  `graph_type_id` tinyint(3) NOT NULL DEFAULT '0',
  `cdef_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `consolidation_function_id` tinyint(2) NOT NULL DEFAULT '0',
  `text_format` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL,
  `hard_return` char(2) DEFAULT NULL,
  `gprint_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `sequence` mediumint(8) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `graph_template_id` (`graph_template_id`),
  KEY `local_graph_id` (`local_graph_id`),
  KEY `task_item_id` (`task_item_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

LOCK TABLES `graph_templates_item` WRITE;
INSERT INTO `graph_templates_item` VALUES
(1234,'',145348,1111,2,27038,94,99,7,2,1,'Descarga:','','',2,6),
(1235,'',135866,1111,2,27038,0,'FF',9,2,4,'Actual:','','',2,1),
(181079,'',145348,13882,2,27038,94,99,7,2,1,'Descarga:','','',2,6),
(181080,'',135866,13882,2,27038,0,'FF',9,2,4,'Actual:','','',2,1),
(181081,'',11,13882,2,27038,0,'FF',9,2,1,'Average:','','',2,7),
(181082,'',12,13882,2,27038,0,'FF',9,2,3,'Maximum:','','on',2,8),
(181087,'',166639,13882,2,27038,0,'FF',1,0,1,'Total In:  |sum:auto:current:2:auto|','','on',2,10),
(181083,'',150081,13882,2,27039,75,'CC',7,2,1,'Subida:','','',2,2),
(181084,'',14,13882,2,27039,0,'FF',9,2,4,'Current:','','',2,3),
(181085,'',15,13882,2,27039,0,'FF',9,2,1,'Average:','','',2,4),
(181086,'',16,13882,2,27039,0,'FF',9,2,3,'Maximum:','','on',2,5),
(181088,'',171046,13882,2,27039,0,'FF',4,18,1,'Total Out:  |sum:auto:current:2:auto|','','',2,11);
UNLOCK TABLES;

CREATE TABLE `data_template_rrd` (
  `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `hash` varchar(32) NOT NULL DEFAULT '',
  `local_data_template_rrd_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `local_data_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `data_template_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `t_rrd_maximum` char(2) DEFAULT NULL,
  `rrd_maximum` varchar(20) NOT NULL DEFAULT '0',
  `t_rrd_minimum` char(2) DEFAULT NULL,
  `rrd_minimum` varchar(20) NOT NULL DEFAULT '0',
  `t_rrd_heartbeat` char(2) DEFAULT NULL,
  `rrd_heartbeat` mediumint(6) NOT NULL DEFAULT '0',
  `t_data_source_type_id` char(2) DEFAULT NULL,
  `data_source_type_id` smallint(5) NOT NULL DEFAULT '0',
  `t_data_source_name` char(2) DEFAULT NULL,
  `data_source_name` varchar(19) NOT NULL DEFAULT '',
  `t_data_input_field_id` char(2) DEFAULT NULL,
  `data_input_field_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `duplicate_dsname_contraint` (`local_data_id`,`data_source_name`,`data_template_id`),
  KEY `local_data_id` (`local_data_id`),
  KEY `data_template_id` (`data_template_id`),
  KEY `local_data_template_rrd_id` (`local_data_template_rrd_id`),
  KEY `data_source_name` (`data_source_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

LOCK TABLES `data_template_rrd` WRITE;
INSERT INTO `data_template_rrd` VALUES
(27038,'',54,13744,41,NULL,'|query_ifSpeed|',NULL,0,NULL,600,NULL,2,NULL,'test_data_source',NULL,0),
(27039,'',55,13744,41,NULL,'|query_ifSpeed|',NULL,0,NULL,600,NULL,2,NULL,'traffic_out',NULL,0);
UNLOCK TABLES;

CREATE TABLE `host_snmp_cache` (
  `host_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `snmp_query_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `field_name` varchar(50) NOT NULL DEFAULT '',
  `field_value` varchar(255) DEFAULT NULL,
  `snmp_index` varchar(255) NOT NULL DEFAULT '',
  `oid` text NOT NULL,
  `present` tinyint(4) NOT NULL DEFAULT '1',
  PRIMARY KEY (`host_id`,`snmp_query_id`,`field_name`,`snmp_index`),
  KEY `host_id` (`host_id`,`field_name`),
  KEY `snmp_index` (`snmp_index`),
  KEY `field_name` (`field_name`),
  KEY `field_value` (`field_value`),
  KEY `snmp_query_id` (`snmp_query_id`),
  KEY `present` (`present`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

LOCK TABLES `host_snmp_cache` WRITE;
INSERT INTO `host_snmp_cache` VALUES
(1008,1,'ifIndex','9','9','.1.3.6.1.2.1.2.2.1.1.9','1'),
(1008,1,'ifOperStatus','Up','9','.1.3.6.1.2.1.2.2.1.8.9','1'),
(1008,1,'ifDescr','GigabitEthernet0/4','9','.1.3.6.1.2.1.2.2.1.2.9','1'),
(1008,1,'ifName','Gi0/4','9','.1.3.6.1.2.1.31.1.1.1.1.9','1'),
(1008,1,'ifAlias','ENoB-Id ','9','.1.3.6.1.2.1.31.1.1.1.18.9','1'),
(1008,1,'ifType','6','9','.1.3.6.1.2.1.2.2.1.3.9','1'),
(1008,1,'ifSpeed','1000000000','9','.1.3.6.1.2.1.2.2.1.5.9','1'),
(1008,1,'ifHighSpeed','1000','9','.1.3.6.1.2.1.31.1.1.1.15.9','1'),
(1008,1,'ifHwAddr','00:3A:9B:35:DA:FC','9','.1.3.6.1.2.1.2.2.1.6.9','1');
UNLOCK TABLES;

CREATE TABLE `graph_templates_graph` (
  `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `local_graph_template_graph_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `local_graph_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `graph_template_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `t_image_format_id` char(2) DEFAULT '0',
  `image_format_id` tinyint(1) NOT NULL DEFAULT '0',
  `t_title` char(2) DEFAULT '0',
  `title` varchar(255) NOT NULL DEFAULT '',
  `title_cache` varchar(255) NOT NULL DEFAULT '',
  `t_height` char(2) DEFAULT '0',
  `height` mediumint(8) NOT NULL DEFAULT '0',
  `t_width` char(2) DEFAULT '0',
  `width` mediumint(8) NOT NULL DEFAULT '0',
  `t_upper_limit` char(2) DEFAULT '0',
  `upper_limit` varchar(20) NOT NULL DEFAULT '0',
  `t_lower_limit` char(2) DEFAULT '0',
  `lower_limit` varchar(20) NOT NULL DEFAULT '0',
  `t_vertical_label` char(2) DEFAULT '0',
  `vertical_label` varchar(200) DEFAULT NULL,
  `t_slope_mode` char(2) DEFAULT '0',
  `slope_mode` char(2) DEFAULT 'on',
  `t_auto_scale` char(2) DEFAULT '0',
  `auto_scale` char(2) DEFAULT NULL,
  `t_auto_scale_opts` char(2) DEFAULT '0',
  `auto_scale_opts` tinyint(1) NOT NULL DEFAULT '0',
  `t_auto_scale_log` char(2) DEFAULT '0',
  `auto_scale_log` char(2) DEFAULT NULL,
  `t_scale_log_units` char(2) DEFAULT '0',
  `scale_log_units` char(2) DEFAULT NULL,
  `t_auto_scale_rigid` char(2) DEFAULT '0',
  `auto_scale_rigid` char(2) DEFAULT NULL,
  `t_auto_padding` char(2) DEFAULT '0',
  `auto_padding` char(2) DEFAULT NULL,
  `t_base_value` char(2) DEFAULT '0',
  `base_value` mediumint(8) NOT NULL DEFAULT '0',
  `t_grouping` char(2) DEFAULT '0',
  `grouping` char(2) NOT NULL DEFAULT '',
  `t_export` char(2) DEFAULT '0',
  `export` char(2) DEFAULT NULL,
  `t_unit_value` char(2) DEFAULT '0',
  `unit_value` varchar(20) DEFAULT NULL,
  `t_unit_exponent_value` char(2) DEFAULT '0',
  `unit_exponent_value` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `local_graph_id` (`local_graph_id`),
  KEY `graph_template_id` (`graph_template_id`),
  KEY `title_cache` (`title_cache`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

LOCK TABLES `graph_templates_graph` WRITE;
INSERT INTO `graph_templates_graph` VALUES
(12345,2,1111,2,0,1,0,'|host_description|-|query_ifName|-|query_ifAlias|-IP |query_ifIP| - graph2','390257-some_host-Gi0/4-ENoB-Id-IP |query_ifIP|',0,120,0,600,0,100,0,0,0,'bits per second',0,'on',0,'on',0,1,0,'',0,'',0,'on',0,'on',0,1000,0,'',0,'on',0,'',0,''),
(13968,2,13882,2,0,1,0,'|host_description|-|query_ifName|-|query_ifAlias|-IP |query_ifIP|','390257-some_host-Gi0/4-ENoB-Id-IP |query_ifIP|',0,120,0,600,0,100,0,0,0,'bits per second',0,'on',0,'on',0,1,0,'',0,'',0,'on',0,'on',0,1000,0,'',0,'on',0,'',0,'');
UNLOCK TABLES;

CREATE TABLE `graph_local` (
  `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `graph_template_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `host_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `snmp_query_id` mediumint(8) NOT NULL DEFAULT '0',
  `snmp_index` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `host_id` (`host_id`),
  KEY `graph_template_id` (`graph_template_id`),
  KEY `snmp_query_id` (`snmp_query_id`),
  KEY `snmp_index` (`snmp_index`)
) ENGINE=MyISAM AUTO_INCREMENT=15002 DEFAULT CHARSET=latin1;

LOCK TABLES `graph_local` WRITE;
INSERT INTO `graph_local` VALUES
(1111,2,1008,1,9),
(13882,2,1008,1,9);
UNLOCK TABLES;

CREATE TABLE `cdef_items` (
  `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `hash` varchar(32) NOT NULL DEFAULT '',
  `cdef_id` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `sequence` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `type` tinyint(2) NOT NULL DEFAULT '0',
  `value` varchar(150) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `cdef_id` (`cdef_id`)
) ENGINE=MyISAM AUTO_INCREMENT=48 DEFAULT CHARSET=latin1;

LOCK TABLES `cdef_items` WRITE;
INSERT INTO `cdef_items` VALUES
(7,'9bbf6b792507bb9bb17d2af0970f9be9',2,1,4,'CURRENT_DATA_SOURCE'),
(9,'a4b8eb2c3bf4920a3ef571a7a004be53',2,2,6,8),
(8,'caa4e023ac2d7b1c4b4c8c4adfd55dfe',2,3,2,3),
(32,'82b2966f515fc959cc51d753d0e082d2',18,1,6,'SIMILAR_DATA_SOURCES_NODUPS,8,*,-1,*');
UNLOCK TABLES;
