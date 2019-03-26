MongoDB
=======================

Supported versions: MongoDB 3.0+


Source config
-------------
- *Connection string* - database connection string e.g. :code:`mongodb://mongo:27017`
- *Username*
- *Password*
- *Authentication Source* - for delegated authentication, specify alternate database name. Leave blank for normal authentication
- *Database*
- *Collection*
- *Is collection capped* - default "no"
- *Initial offset* - Date or id from witch to pull data from
- *Offset type* - :code:`OBJECTID`, :code:`STRING` or  :code:`DATE`. Default - :code:`OBJECTID`
- *Offset field* - default :code:`_id`
- *Batch size* - how many records to send to further pipeline stages. Default - 1000 records
- *Max batch wait time (seconds)* - how many time to wait until batch will reach it's size. Default - 5 seconds



Pipeline config
---------------
- *Pipeline ID* - unique pipeline identifier (use human-readable name so you could easily use it further)
- *Measurement name* - what do you measure (this will be the value of :code:`what` property in anodot 2.0 metric protocol)
- Values config
    - Basic
        - *Value* - enter property name
    - Advanced
        - *Value type* - property or constant
        - *Value* - if type property - enter property name, if type constant - enter value
- *Target type* - represents how samples of the same metric are aggregated in Anodot. Valid values are: :code:`gauge` (average aggregation), :code:`counter` (sum aggregation). Deafult - :code:`gauge`
- *Timestamp property name*
- *Timestamp property type* - default :code:`unix`
    - :code:`string` (must specify format)
    - :code:`datetime` (if property has database specific datetime type like `Date` in mongo)
    - :code:`unix_ms` (unix timestamp in milliseconds)
    - :code:`unix` (unix timestamp in seconds)
- *Timestamp format string* - if timestamp property type is string - specify format according to this [spec](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html).
- *Required dimensions* - Names of properties delimited with spaces. If these fields are missing in a record, it goes to error stage
- *Optional dimensions* - Names of properties delimited with spaces. These fields may be missing in a record

If your JSON data has nested structure you can specify path to required field with :code:`/` sign. For example:

.. code-block:: json

    {
      "transaction": {
        "type": "SALE",
        "status": "SUCCESS"
      }
    }

To specify these fields in pipeline config you can type :code:`transaction/type` and :code:`transaction/status`
