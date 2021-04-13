CREATE DATABASE if not exists test;

CREATE TABLE if not exists test.test(
    id INT,
    timestamp_unix Int32,
    timestamp_unix_ms Int64,
    ver String,
    adsize String,
    country Nullable(String),
    adtype String,
    exchange String,
    clicks Nullable(Float64),
    impressions Nullable(Int32),
    timestamp_datetime DateTime('Etc/UTC'),
    timestamp_string String
) ENGINE = MergeTree()
PRIMARY KEY id;

INSERT INTO test.test (timestamp_unix,timestamp_unix_ms,ver,adsize,country,adtype,exchange,clicks,impressions,timestamp_datetime,timestamp_string)
VALUES (1512867600,1512867600000,'AD200',' Sma.ll ','USA','Display','DoubleClick',6784.69,123,'2017-12-10 01:00:00','12/10/2017 1:00:00');

INSERT INTO test.test (timestamp_unix,timestamp_unix_ms,ver,adsize,country,adtype,exchange,clicks,impressions,timestamp_datetime,timestamp_string)
VALUES (1512871200,1512871200000,'AD200','Sma.ll','USA','Display','DoubleClick',6839,22,'2017-12-10 02:00:00','12/10/2017 2:00:00');

INSERT INTO test.test (timestamp_unix,timestamp_unix_ms,ver,adsize,country,adtype,exchange,clicks,impressions,timestamp_datetime,timestamp_string)
VALUES (1512874800,1512874800000,'AD200','Sma.ll','USA','Display','DoubleClick',690999,15,'2017-12-10 03:00:00','12/10/2017 3:00:00');

INSERT INTO test.test (timestamp_unix,timestamp_unix_ms,ver,adsize,country,adtype,exchange,clicks,impressions,timestamp_datetime,timestamp_string)
VALUES (1512878400,1512878400000,'AD200','Sma.ll','USA','Display','DoubleClick',7158.97,3,'2017-12-10 04:00:00','12/10/2017 4:00:00');

INSERT INTO test.test (timestamp_unix,timestamp_unix_ms,ver,adsize,country,adtype,exchange,clicks,impressions,timestamp_datetime,timestamp_string)
VALUES (1512885600,1512885600000,'AD200','Sma ll','USA','Display','DoubleClick',NULL,4,'2017-12-10 06:00:00','12/10/2017 6:00:00');

INSERT INTO test.test (timestamp_unix,timestamp_unix_ms,ver,adsize,country,adtype,exchange,clicks,impressions,timestamp_datetime,timestamp_string)
VALUES (1512889200,1512889200000,'AD200','Sma ll',NULL,'Display','DoubleClick',7427.77,0,'2017-12-10 07:00:00','12/10/2017 7:00:00');
