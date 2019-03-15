InfluxDB
=======================


Source config
-------------
- *InfluxDB API url*
- *Database*
- *Limit* - max values returned in one query. Default - 1000
- *Initial offset* - integer, default 0
- *Wait time* - integer, ms, default 2000



Pipeline config
---------------
- *Pipeline ID* - unique pipeline identifier (use human-readable name so you could easily use it further)
- *Measurement name* - metric name in InfluxDB from which to make query
- Values config
    - Basic
        - *Value* - enter column names, separated with spaces
    - Advanced
        - *Value type* - column or constant
        - *Value* - if type column - enter column names, separated with spaces, if type constant - enter value
- *Target type* - represents how samples of the same metric are aggregated in Anodot. Valid values are: :code:`gauge` (average aggregation), :code:`counter` (sum aggregation)
- Dimensions
    - Basic
        - *Dimensions* - Names of columns delimited with spaces. These fields may be missing in a record
    - Advanced
        - *Required dimensions* - Names of columns delimited with spaces. If these fields are missing in a record, it goes to error stage
        - *Optional dimensions* - Names of columns delimited with spaces. These fields may be missing in a record

Pipeline forms a query :code:`SELECT {dimensions},{values} FROM {measurement} LIMIT {limit} OFFSET {offset}`.
When query result is empty, it waits :code:`Wait time` and makes query again.
