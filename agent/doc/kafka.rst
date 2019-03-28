Kafka
=======================

Supported versions: Kafka 2.0+

Source config
-------------
- *Kafka broker connection string*
- *Consumer group* - default "anodotAgent"
- *Topic* - Kafka topic
- *Initial offset* - values: EARLIEST, LATEST, TIMESTAMP
- *Offset timestamp (unix timestamp in milliseconds)* - if initial offset is TIMESTAMP then specify it here
- (advanced) *Max Batch Size (records)* - how many records to send to further pipeline stages. Default - 1000 records
- (advanced) *Batch Wait Time (ms)* - how many time to wait until batch will reach it's size. Default - 1000 ms
- (advanced) *Kafka Configuration* - Additional Kafka properties to pass to the underlying Kafka consumer. Format - key1:value1 key2:value2 key3:value3

Example:

.. code-block:: console

    > agent source create
    Choose source (mongo, kafka, influx): kafka
    Enter unique name for this source config: kafka_test
    Kafka broker connection string: kafka:9092
    Consumer group [anodotAgent]:
    Topic: test_topic
    Initial offset (EARLIEST, LATEST, TIMESTAMP) [EARLIEST]:
    Source config created
    >
    > agent source create -a
    Choose source (mongo, kafka, influx): kafka
    Enter unique name for this source config: kafka_test
    Kafka broker connection string: kafka:9092
    Consumer group [anodotAgent]:
    Topic: test_topic
    Initial offset (EARLIEST, LATEST, TIMESTAMP) [EARLIEST]:
    Max Batch Size (records) [1000]:
    Batch Wait Time (ms) [1000]:
    Kafka Configuration []: key1:value1 key2:value2 key3:value3
    Source config created



Pipeline config
---------------
- *Pipeline ID* - unique pipeline identifier (use human-readable name so you could easily use it further)
- *Measurement name* - what do you measure (this will be the value of :code:`what` property in anodot 2.0 metric protocol)
- Measurement values config
    - Basic
        - *Value* - enter property name
    - Advanced
        - *Value type* - property (if measurement value is one of data properties) or constant (if measurement value is constant for every record, for example when you measure is records count, so for every record measurement value equals 1)
        - *Value* - if type property - enter property name, if type constant - enter value
- *Target type* - represents how samples of the same metric are aggregated in Anodot. Valid values are: :code:`gauge` (average aggregation), :code:`counter` (sum aggregation). Deafult - :code:`gauge`
- Timestamp config
    - Use kafka timestamp or take it from data it
    - *Timestamp property name*
    - *Timestamp property type* :code:`unix`
        - :code:`string` (must specify format)
        - :code:`unix_ms` (unix timestamp in milliseconds)
        - :code:`unix` (unix timestamp in seconds)
    - *Timestamp format string* - if timestamp property type is string - specify format according to this [spec](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html).
- *Required dimensions* - Names of properties delimited with spaces. If these fields are missing in a record, it goes to error stage
- *Optional dimensions* - Names of properties delimited with spaces. These fields may be missing in a record

If your JSON data has nested structure you can specify path to required field with :code:`/` sign. For example:

.. code-block:: json

    {
      "amount": 100,
      "transaction": {
        "type": "SALE",
        "status": "SUCCESS"
      }
    }

To specify these fields in pipeline config you can type :code:`transaction/type` and :code:`transaction/status`

Example:

.. code-block:: console

    > agent pipeline create
    Choose source config (kafka_test): kafka_test
    Choose destination (http) [http]:
    Pipeline ID (must be unique): test
    Measurement name: transactions_amount
    Value property name: amount
    Target type (counter, gauge) [gauge]:
    Use kafka timestamp? [y/N]: y
    Required dimensions [[]]: transaction/type
    Optional dimensions [[]]: transaction/status
    Created pipeline test
    >
    > agent pipeline create -a
    Choose source config (kafka_test): kafka_test
    Choose destination (http) [http]:
    Pipeline ID (must be unique): test
    Measurement name: transactions_count
    Value (property name or constant value): 1
    Value type (property, constant): constant
    Target type (counter, gauge) [gauge]: counter
    Use kafka timestamp? [y/N]: N
    Timestamp property name: time
    Timestamp property type (string, unix, unix_ms) [unix]: string
    Timestamp format string: yyyy-MM-dd'T'HH:mm:ss.SSSZ
    Required dimensions [[]]: transaction/type transaction/status
    Optional dimensions [[]]:
    Created pipeline test


