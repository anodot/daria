CREATE DATABASE test;
USE test;

CREATE TABLE test(
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp_unix INT,
    timestamp_unix_ms BIGINT,
    ver INT,
    adsize VARCHAR(20),
    country VARCHAR(20),
    adtype VARCHAR(20),
    exchange VARCHAR(20),
    clicks FLOAT,
    impressions INT,
    timestamp_datetime DATETIME,
    timestamp_string VARCHAR(30)
);
INSERT INTO test (timestamp_unix,timestamp_unix_ms,ver,adsize,country,adtype,exchange,clicks,impressions,timestamp_datetime,timestamp_string)
VALUES (1512867600,1512867600000,1,' Sma.ll ','USA','Display','DoubleClick',6784.69,123,'2017-12-10 1:00:00','12/10/2017 1:00:00'),
       (1512871200,1512871200000,1,'Sma.ll','USA','Display','DoubleClick',6839,22,'2017-12-10 2:00:00','12/10/2017 2:00:00'),
       (1512874800,1512874800000,1,'Sma.ll','USA','Display','DoubleClick',690999,15,'2017-12-10 3:00:00','12/10/2017 3:00:00'),
       (1512878400,1512878400000,1,'Sma ll','USA','Display','DoubleClick',7158.97,3,'2017-12-10 4:00:00','12/10/2017 4:00:00'),
       (1512885600,1512885600000,1,'Sma ll','USA','Display','DoubleClick',NULL,4,'2017-12-10 6:00:00','12/10/2017 6:00:00'),
       (1512889200,1512889200000,1,'Sma ll',NULL,'Display','DoubleClick',7427.77,0,'2017-12-10 7:00:00','12/10/2017 7:00:00');
