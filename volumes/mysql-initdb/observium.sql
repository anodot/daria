CREATE DATABASE observium;
USE observium;

DROP TABLE IF EXISTS `devices_locations`;
CREATE TABLE `devices_locations` (
  `location_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `device_id` int(11) NOT NULL,
  `location` text COLLATE utf8_unicode_ci,
  `location_lat` decimal(10,7) DEFAULT NULL,
  `location_lon` decimal(10,7) DEFAULT NULL,
  `location_country` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `location_state` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `location_county` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `location_city` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `location_geoapi` varchar(16) CHARACTER SET latin1 COLLATE latin1_general_ci DEFAULT NULL,
  `location_status` text COLLATE utf8_unicode_ci,
  `location_manual` tinyint(1) NOT NULL DEFAULT '0',
  `location_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`location_id`),
  UNIQUE KEY `device_id` (`device_id`)
) ENGINE=InnoDB AUTO_INCREMENT=185 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='Stores geo location information';

LOCK TABLES `devices_locations` WRITE;
INSERT INTO `devices_locations`
VALUES (2, 1, 'SOME-LOC', NULL, NULL, NULL, NULL, NULL, NULL, 'geocode', 'Geocoding ENABLED', 0, '2021-01-01 00:00:00');
UNLOCK TABLES;

DROP TABLE IF EXISTS `devices`;
 CREATE TABLE `devices` (
  `device_id` int(11) NOT NULL AUTO_INCREMENT,
  `poller_id` int(11) NOT NULL DEFAULT '0',
  `hostname` varchar(253) COLLATE utf8_unicode_ci NOT NULL,
  `sysName` varchar(253) COLLATE utf8_unicode_ci DEFAULT NULL,
  `label` varchar(253) CHARACTER SET utf8 DEFAULT NULL,
  `ip` varchar(128) CHARACTER SET latin1 COLLATE latin1_general_ci DEFAULT NULL,
  `snmp_community` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `snmp_authlevel` enum('noAuthNoPriv','authNoPriv','authPriv') CHARACTER SET latin1 COLLATE latin1_general_ci DEFAULT NULL,
  `snmp_authname` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `snmp_authpass` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `snmp_authalgo` enum('MD5','SHA','SHA-224','SHA-256','SHA-384','SHA-512') CHARACTER SET latin1 COLLATE latin1_general_ci DEFAULT NULL,
  `snmp_cryptopass` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `snmp_cryptoalgo` enum('DES','AES','AES-192','AES-192-C','AES-256','AES-256-C') CHARACTER SET latin1 COLLATE latin1_general_ci DEFAULT NULL,
  `snmp_context` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `snmp_version` enum('v1','v2c','v3') CHARACTER SET latin1 COLLATE latin1_general_ci NOT NULL DEFAULT 'v2c',
  `snmp_port` smallint(5) unsigned NOT NULL DEFAULT '161',
  `snmp_timeout` int(11) DEFAULT NULL,
  `snmp_retries` int(11) DEFAULT NULL,
  `snmp_maxrep` int(11) DEFAULT NULL,
  `ssh_port` int(11) NOT NULL DEFAULT '22',
  `agent_version` int(11) DEFAULT NULL,
  `snmp_transport` enum('udp','tcp','udp6','tcp6') CHARACTER SET latin1 COLLATE latin1_general_ci NOT NULL DEFAULT 'udp',
  `bgpLocalAs` int(11) unsigned DEFAULT NULL,
  `snmpEngineID` varchar(255) CHARACTER SET latin1 COLLATE latin1_general_ci DEFAULT NULL,
  `sysObjectID` varchar(255) CHARACTER SET latin1 COLLATE latin1_general_ci DEFAULT NULL,
  `sysDescr` text COLLATE utf8_unicode_ci,
  `sysContact` text COLLATE utf8_unicode_ci,
  `version` text COLLATE utf8_unicode_ci,
  `hardware` text COLLATE utf8_unicode_ci,
  `vendor` varchar(255) CHARACTER SET utf8 DEFAULT NULL COMMENT 'Hardware vendor',
  `features` text COLLATE utf8_unicode_ci,
  `location` text COLLATE utf8_unicode_ci,
  `os` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `status` tinyint(4) NOT NULL DEFAULT '0',
  `status_type` enum('ping','snmp','dns','ok') CHARACTER SET latin1 COLLATE latin1_general_ci NOT NULL DEFAULT 'ok',
  `ignore` tinyint(4) NOT NULL DEFAULT '0',
  `ignore_until` datetime DEFAULT NULL,
  `asset_tag` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `disabled` tinyint(1) NOT NULL DEFAULT '0',
  `uptime` int(11) unsigned DEFAULT NULL,
  `last_rebooted` int(10) unsigned DEFAULT NULL,
  `force_discovery` tinyint(1) NOT NULL DEFAULT '0',
  `last_polled` timestamp NULL DEFAULT NULL,
  `last_discovered` timestamp NULL DEFAULT NULL,
  `last_alerter` timestamp NULL DEFAULT NULL,
  `last_polled_timetaken` double(5,2) DEFAULT NULL,
  `last_discovered_timetaken` double(5,2) DEFAULT NULL,
  `purpose` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `type` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `serial` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `icon` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `device_state` text COLLATE utf8_unicode_ci,
  `distro` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `distro_ver` varchar(16) COLLATE utf8_unicode_ci DEFAULT NULL,
  `kernel` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `arch` varchar(8) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`device_id`),
  UNIQUE KEY `hostname` (`hostname`) USING BTREE,
  KEY `status` (`status`),
  KEY `sysName` (`sysName`),
  KEY `os` (`os`),
  KEY `ignore` (`ignore`),
  KEY `disabled_lastpolled` (`disabled`,`last_polled_timetaken`)
) ENGINE=InnoDB AUTO_INCREMENT=185 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

LOCK TABLES `devices` WRITE;
INSERT INTO `devices`
VALUES (1, 0, 'host1', 'sys1', 'lable', '192.168.0.1', 'public', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'v2c', '161', NULL, NULL, NULL, 22, NULL, 'udp', 65505, '234789798FG43', '.1.3.6.1.4.1.1.12.29', 'Juniper Networks, Inc.', 'Some Team', '10.0', 'HJ73E', 'Juniper', 'Internet Router', 'SOME-LOC', 'alpine', 1, 'ok', 0, NULL, NULL, 0, 1000, 1607830000, 0, '2021-01-01 00:00:00', '2021-01-01 00:00:00', '2021-01-01 00:00:00', 22.11, 80.21, NULL, 'network', 'HSNC749SKN', NULL, NULL, NULL, NULL, NULL, NULL);
UNLOCK TABLES;

DROP TABLE IF EXISTS `ports`;
CREATE TABLE `ports` (
  `port_id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) NOT NULL DEFAULT '0',
  `port_64bit` tinyint(1) DEFAULT NULL,
  `port_label` varchar(128) DEFAULT NULL,
  `port_label_base` varchar(128) DEFAULT NULL,
  `port_label_num` varchar(64) DEFAULT NULL,
  `port_label_short` varchar(96) DEFAULT NULL,
  `port_descr_type` varchar(24) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `port_descr_descr` varchar(255) DEFAULT NULL,
  `port_descr_circuit` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `port_descr_speed` varchar(32) DEFAULT NULL,
  `port_descr_notes` varchar(255) DEFAULT NULL,
  `ifDescr` varchar(255) DEFAULT NULL,
  `ifName` varchar(64) DEFAULT NULL,
  `ifIndex` int(11) unsigned NOT NULL,
  `ifSpeed` bigint(20) DEFAULT NULL,
  `ifConnectorPresent` varchar(12) DEFAULT NULL,
  `ifPromiscuousMode` varchar(12) DEFAULT NULL,
  `ifHighSpeed` int(10) unsigned DEFAULT NULL,
  `ifOperStatus` enum('testing','notPresent','dormant','down','lowerLayerDown','unknown','up','monitoring') CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `ifAdminStatus` enum('down','up','testing') CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `ifDuplex` varchar(12) DEFAULT NULL,
  `ifMtu` int(11) DEFAULT NULL,
  `ifType` varchar(32) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `ifAlias` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `ifPhysAddress` varchar(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `ifHardType` varchar(64) DEFAULT NULL,
  `ifLastChange` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ifVlan` varchar(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `ifTrunk` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `ifVrf` int(16) DEFAULT NULL,
  `encrypted` tinyint(1) NOT NULL DEFAULT '0',
  `ignore` tinyint(1) NOT NULL DEFAULT '0',
  `disabled` tinyint(1) NOT NULL DEFAULT '0',
  `detailed` tinyint(1) NOT NULL DEFAULT '0',
  `deleted` tinyint(1) NOT NULL DEFAULT '0',
  `ifInUcastPkts` bigint(20) unsigned DEFAULT NULL,
  `ifInUcastPkts_rate` bigint(20) unsigned NOT NULL DEFAULT '0',
  `ifOutUcastPkts` bigint(20) unsigned DEFAULT NULL,
  `ifOutUcastPkts_rate` bigint(20) unsigned NOT NULL DEFAULT '0',
  `ifInErrors` bigint(20) unsigned DEFAULT NULL,
  `ifInErrors_rate` float unsigned NOT NULL DEFAULT '0',
  `ifOutErrors` bigint(20) unsigned DEFAULT NULL,
  `ifOutErrors_rate` float unsigned NOT NULL DEFAULT '0',
  `ifOctets_rate` bigint(20) unsigned NOT NULL DEFAULT '0',
  `ifUcastPkts_rate` bigint(20) unsigned NOT NULL DEFAULT '0',
  `ifErrors_rate` float unsigned NOT NULL DEFAULT '0',
  `ifInOctets` bigint(20) unsigned DEFAULT NULL,
  `ifInOctets_rate` bigint(20) unsigned NOT NULL DEFAULT '0',
  `ifOutOctets` bigint(20) unsigned DEFAULT NULL,
  `ifOutOctets_rate` bigint(20) unsigned NOT NULL DEFAULT '0',
  `ifInOctets_perc` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `ifOutOctets_perc` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `poll_time` int(11) unsigned NOT NULL DEFAULT '0',
  `poll_period` int(11) unsigned NOT NULL DEFAULT '300',
  `ifInErrors_delta` int(10) unsigned NOT NULL DEFAULT '0',
  `ifOutErrors_delta` int(10) unsigned NOT NULL DEFAULT '0',
  `ifInNUcastPkts` bigint(20) unsigned DEFAULT NULL,
  `ifInNUcastPkts_rate` int(10) unsigned NOT NULL DEFAULT '0',
  `ifOutNUcastPkts` bigint(20) unsigned DEFAULT NULL,
  `ifOutNUcastPkts_rate` int(10) unsigned NOT NULL DEFAULT '0',
  `ifInBroadcastPkts` bigint(20) unsigned DEFAULT NULL,
  `ifInBroadcastPkts_rate` int(10) unsigned NOT NULL DEFAULT '0',
  `ifOutBroadcastPkts` bigint(20) unsigned DEFAULT NULL,
  `ifOutBroadcastPkts_rate` int(10) unsigned NOT NULL DEFAULT '0',
  `ifInMulticastPkts` bigint(20) unsigned DEFAULT NULL,
  `ifInMulticastPkts_rate` int(10) unsigned NOT NULL DEFAULT '0',
  `ifOutMulticastPkts` bigint(20) unsigned DEFAULT NULL,
  `ifOutMulticastPkts_rate` int(10) unsigned NOT NULL DEFAULT '0',
  `port_mcbc` tinyint(1) DEFAULT NULL,
  `ifInDiscards` bigint(20) unsigned DEFAULT NULL,
  `ifInDiscards_rate` float unsigned NOT NULL DEFAULT '0',
  `ifOutDiscards` bigint(20) unsigned DEFAULT NULL,
  `ifOutDiscards_rate` float unsigned NOT NULL DEFAULT '0',
  `ifDiscards_rate` float unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`port_id`),
  UNIQUE KEY `device_ifIndex` (`device_id`,`ifIndex`),
  KEY `if_2` (`ifDescr`),
  KEY `port_cache` (`port_id`,`device_id`,`ignore`,`deleted`,`ifOperStatus`,`ifAdminStatus`),
  KEY `device_cache` (`device_id`,`disabled`,`deleted`)
) ENGINE=InnoDB AUTO_INCREMENT=35541 DEFAULT CHARSET=utf8;

LOCK TABLES `ports` WRITE;
INSERT INTO `ports`
VALUES (1, 1, 1, 'ia', 'gst', 0, 'gst0', NULL, NULL, NULL, NULL, NULL, 'gst0.300', 'gst0', 1, 10000000, 'true', 'false', 10, 'down', 'up', NULL, 1514, 'ethernet.Anodot', 'EthAlias', '00fd665sd', NULL, '2021-01-01 00:00:00', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0, 0, 100500, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1628160620, 299, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0),
         (2, 1, 1, 'nv', 'grm', NULL, 'mrm', NULL, NULL, NULL, NULL, NULL, 'dsc', 'dsc', 5, 0, 'false', 'false', 0, 'up', 'up', NULL, 89524542, 'other', '', NULL, NULL, '2021-01-01 00:00:00', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0, 0, 100400, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1628160620, 299, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0),
         (3, 1, 1, 'ny', 'gst', 0, 'gst0', NULL, NULL, NULL, NULL, NULL, 'gst0.300', 'gst0', 6, 0, 'true', 'false', 10, 'down', 'up', NULL, 1514, 'other', '', '00adf0fsd7', NULL, '2021-01-01 00:00:00', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0, 0, 100400, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1628160620, 299, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0);
UNLOCK TABLES;

DROP TABLE IF EXISTS `mempools`;
 CREATE TABLE `mempools` (
  `mempool_id` int(11) NOT NULL AUTO_INCREMENT,
  `mempool_index` varchar(128) CHARACTER SET latin1 COLLATE latin1_general_ci NOT NULL,
  `entPhysicalIndex` int(11) DEFAULT NULL,
  `hrDeviceIndex` int(11) DEFAULT NULL,
  `mempool_mib` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `mempool_multiplier` float(14,5) NOT NULL DEFAULT '1.00000',
  `mempool_hc` tinyint(1) NOT NULL DEFAULT '0',
  `mempool_descr` varchar(255) CHARACTER SET utf8 NOT NULL,
  `device_id` int(11) NOT NULL,
  `mempool_deleted` tinyint(1) NOT NULL DEFAULT '0',
  `mempool_warn_limit` int(11) DEFAULT NULL,
  `mempool_crit_limit` int(11) DEFAULT NULL,
  `mempool_ignore` int(11) DEFAULT NULL,
  `mempool_table` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `mempool_polled` int(11) NOT NULL,
  `mempool_perc` int(11) NOT NULL,
  `mempool_used` bigint(16) NOT NULL,
  `mempool_free` bigint(16) NOT NULL,
  `mempool_total` bigint(16) NOT NULL,
  PRIMARY KEY (`mempool_id`),
  KEY `device_id` (`device_id`)
) ENGINE=InnoDB AUTO_INCREMENT=814 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

LOCK TABLES `mempools` WRITE;
INSERT INTO `mempools`
VALUES (1, 1253.1, null, null, null, 1.00000, 0, 'Module 1 (Processor)', 1, 0, null, null, null, '', 1628160603, 21, 43289060, 163147772, 206436832);
UNLOCK TABLES;

DROP TABLE IF EXISTS `storage`;
 CREATE TABLE `storage` (
  `storage_id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) NOT NULL,
  `storage_mib` varchar(64) CHARACTER SET latin1 COLLATE latin1_general_ci DEFAULT NULL,
  `storage_index` varchar(128) CHARACTER SET latin1 COLLATE latin1_general_ci NOT NULL,
  `storage_type` varchar(32) CHARACTER SET latin1 COLLATE latin1_general_cs DEFAULT NULL,
  `storage_descr` text CHARACTER SET utf8 NOT NULL,
  `storage_hc` tinyint(1) NOT NULL DEFAULT '0',
  `storage_deleted` tinyint(1) NOT NULL DEFAULT '0',
  `storage_warn_limit` int(11) DEFAULT '0',
  `storage_crit_limit` int(11) DEFAULT '0',
  `storage_ignore` tinyint(1) NOT NULL DEFAULT '0',
  `storage_polled` int(11) NOT NULL,
  `storage_size` bigint(20) NOT NULL,
  `storage_units` int(11) NOT NULL,
  `storage_used` bigint(20) NOT NULL,
  `storage_free` bigint(20) NOT NULL,
  `storage_perc` int(11) NOT NULL,
  `my own field` int(11) NOT NULL,
  PRIMARY KEY (`storage_id`),
  UNIQUE KEY `index_unique` (`device_id`,`storage_mib`,`storage_index`),
  KEY `device_id` (`device_id`)
) ENGINE=InnoDB AUTO_INCREMENT=966 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

LOCK TABLES `storage` WRITE;
INSERT INTO `storage`
VALUES (1, 1, 'HOST-RESOURCES-MIB', 1, 'flashMemory', 'description', 0, 0, NULL, NULL, 0, 1633518002, 9223372036854775807, 2048, 47782296, 44979816, 52, 42);
UNLOCK TABLES;

DROP TABLE IF EXISTS `processors`;
 CREATE TABLE `processors` (
  `processor_id` int(11) NOT NULL AUTO_INCREMENT,
  `entPhysicalIndex` int(11) DEFAULT NULL,
  `hrDeviceIndex` int(11) DEFAULT NULL,
  `device_id` int(11) NOT NULL,
  `processor_oid` varchar(128) CHARACTER SET latin1 COLLATE latin1_general_ci NOT NULL,
  `processor_index` varchar(128) CHARACTER SET latin1 COLLATE latin1_general_ci NOT NULL,
  `processor_type` varchar(64) CHARACTER SET latin1 COLLATE latin1_general_cs NOT NULL,
  `processor_descr` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `processor_returns_idle` tinyint(1) NOT NULL DEFAULT '0',
  `processor_precision` int(11) NOT NULL DEFAULT 1,
  `processor_warn_limit` int(11) DEFAULT NULL,
  `processor_warn_count` int(11) DEFAULT NULL,
  `processor_crit_limit` int(11) DEFAULT NULL,
  `processor_crit_count` int(11) DEFAULT NULL,
  `processor_usage` int(11) NOT NULL,
  `processor_polled` int(11) NOT NULL,
  `processor_ignore` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`processor_id`),
  KEY `device_id` (`device_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1207 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

LOCK TABLES `processors` WRITE;
INSERT INTO `processors`
VALUES (1, 187073, NULL, 1, '.1.3.6.1.9.1.1.1.1.1.1.1', 202, 'cpm', 'description', 0, 1, NULL, NULL, NULL, NULL, 3, 1633517705, 0);
UNLOCK TABLES;

DROP TABLE IF EXISTS `mempools_lookup`;
CREATE TABLE `mempools_lookup`
(
    `id`         int unsigned NOT NULL AUTO_INCREMENT,
    `mempool_id` int          NOT NULL,
    `device_id`  int          NOT NULL,
    `vendor`     varchar(255) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = MyISAM
  DEFAULT CHARSET = latin1;

LOCK TABLES `mempools_lookup` WRITE;
INSERT INTO `mempools_lookup`
VALUES (1, 1, 1, 'Anodot.com');
UNLOCK TABLES;
