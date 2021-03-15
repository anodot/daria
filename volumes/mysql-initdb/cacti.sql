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
) ENGINE=MyISAM AUTO_INCREMENT=14833 DEFAULT CHARSET=latin1;

LOCK TABLES `data_local` WRITE;
INSERT INTO `data_local` VALUES
(13744,41,1008,1,'9');
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
) ENGINE=MyISAM AUTO_INCREMENT=14955 DEFAULT CHARSET=latin1;

LOCK TABLES `data_template_data` WRITE;
INSERT INTO `data_template_data` VALUES
(13866,41,13744,41,2,NULL,'|host_description| - Traffic - |query_ifName| |query_ifAlias|','390257-some_host - Traffic - Gi0/4 ENoB-Id','<path_rra>/test.rrd',NULL,'on',NULL,300,NULL);
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
) ENGINE=MyISAM AUTO_INCREMENT=1104 DEFAULT CHARSET=latin1;

LOCK TABLES `host` WRITE;
INSERT INTO `host` VALUES
(1008,5,'390257-SAPUYO-SAPUYO-CA920-T2','10.20.22.30','','RedIP-SV',2,'','','','','','',161,500,2,1,23,400,3,10,1,'','',1,0,'on','',3,0,'0000-00-00 00:00:00','0000-00-00 00:00:00','Host did not respond to SNMP',1.07550,1519.15000,8.84000,7.28090,124425,150,99.87945,0.000000,0,0,0,'on',0.0000000000,0.0000000000);
UNLOCK TABLES;
