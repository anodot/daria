from enum import Enum
from typing import Type

from agent import source
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, BooleanField, FieldList
from wtforms.validators import DataRequired, URL, Optional, ValidationError


def validate_influx_write_db(form, field):
    if form.write_url.data and not field.data:
        raise ValidationError('Field must not be empty')


def __validate_choice(field, choices):
    if field.data not in choices:
        raise ValidationError(f'{field.data} value is invalid, available values are {", ".join(choices)}')


def validate_kafka_version(_, field):
    __validate_choice(field, ['0.10', '0.11', '2.0+'])


def validate_kafka_offset(_, field):
    __validate_choice(
        field,
        [
            source.KafkaSource.OFFSET_EARLIEST,
            source.KafkaSource.OFFSET_LATEST,
            source.KafkaSource.CONFIG_OFFSET_TIMESTAMP
        ]
    )


def validate_kafka_data_format(_, field):
    __validate_choice(
        field,
        [
            source.KafkaSource.DATA_FORMAT_JSON,
            source.KafkaSource.DATA_FORMAT_CSV,
            source.KafkaSource.DATA_FORMAT_AVRO,
        ]
    )


def validate_kafka_delimited_format(form, field):
    if form.data_format.data == source.KafkaSource.DATA_FORMAT_CSV:
        __validate_choice(
            field,
            [
                source.KafkaSource.CONFIG_CSV_TYPE_DEFAULT,
                source.KafkaSource.CONFIG_CSV_TYPE_CUSTOM,
            ]
        )


def validate_kafka_delimiter(form, field):
    if form.data_format.data == source.KafkaSource.DATA_FORMAT_CSV \
            and form.delimited_format_type.data == source.KafkaSource.CONFIG_CSV_TYPE_CUSTOM:
        if not field.data:
            raise ValidationError('Field must not be empty')


class SourceForm(FlaskForm):
    name = StringField('Name', [DataRequired()])


class Influx(SourceForm):
    host = StringField('InfluxDB API url',
                       [DataRequired(), URL(False, 'Wrong url format, please specify the protocol and domain name')])
    username = StringField('Username')
    password = StringField('Password')
    db = StringField('Database', [DataRequired()])
    write_url = StringField('Write InfluxDB API url', [Optional(), URL()])
    write_username = StringField('Write InfluxDB username')
    write_password = StringField('Write InfluxDB password')
    write_database = StringField('Write InfluxDB database', [validate_influx_write_db])
    initial_offset = IntegerField('Initial offset')


class EditInflux(Influx):
    host = StringField('InfluxDB API url',
                       [Optional(), URL(False, 'Wrong url format, please specify the protocol and domain name')])
    db = StringField('Database')


class Kafka(SourceForm):
    version = StringField('Kafka version', [Optional(), validate_kafka_version])
    broker_uri = StringField('Kafka broker connection string', [DataRequired()])
    #  не очень понятное название
    configuration = StringField('Kafka configuration')
    topics = FieldList(StringField('Topic list', [DataRequired()]), min_entries=1)
    num_of_threads = IntegerField('Number of threads')
    initial_offset = StringField('Initial offset', [Optional(), validate_kafka_offset])
    data_format = StringField('Data format', [Optional(), validate_kafka_data_format])
    # todo change "Change fields names" to override in project?
    delimited_format_type = StringField('Delimited format type', [validate_kafka_delimited_format])
    custom_delimiter_character = StringField('Custom delimiter character', [validate_kafka_delimiter])
    override_field_names = StringField('Override field names')
    max_batch_size = IntegerField('Max batch size (records)')
    batch_wait_time = IntegerField('Batch wait time (ms)')


class EditKafka(Kafka):
    broker_uri = StringField('Kafka broker connection string')
    topics = FieldList(StringField('Topic list', [DataRequired()]))


class Mongo(SourceForm):
    url = StringField('Connection string',
                      [DataRequired(), URL(False, 'Wrong url format, please specify the protocol and domain name')])
    username = StringField('Username')
    password = StringField('Password')
    authentication_source = StringField('Authentication source')
    database = StringField('Database', [DataRequired()])
    collection = StringField('Collection', [DataRequired()])
    is_capped = BooleanField('Is collection capped')
    initial_offset = IntegerField('Initial offset', [DataRequired()])
    offset_type = SelectField('Offset type', choices=[
        source.mongo.MongoSource.OFFSET_TYPE_OBJECT_ID,
        source.mongo.MongoSource.OFFSET_TYPE_STRING,
        source.mongo.MongoSource.OFFSET_TYPE_DATE,
    ])
    offset_field = StringField('Offset field')
    batch_size = IntegerField('Batch size')
    max_batch_wait_seconds = IntegerField('Max batch wait time (seconds)')


class EditMongo(Mongo):
    pass


class MySQL(SourceForm):
    url = StringField('Connection string',
                      [DataRequired(), URL(False, 'Wrong url format, please specify the protocol and domain name')])
    username = StringField('Username')
    password = StringField('Password')


class EditMySQL(MySQL):
    pass


class Postgres(MySQL):
    pass


class EditPostgres(Postgres):
    pass


class Elastic(SourceForm):
    url = StringField('Cluster HTTP URIs',
                      [DataRequired(), URL(False, 'Wrong url format, please specify the protocol and domain name')])
    index = StringField('Index')
    offset_field = StringField('Offset field')
    initial_offset = StringField('Initial offset')
    query_interval = IntegerField('Query interval (seconds)')


class EditElastic(Elastic):
    pass


class Splunk(SourceForm):
    pass


class EditSplunk(Splunk):
    pass


class Directory(SourceForm):
    directory_path = StringField('Directory path', [DataRequired()])
    filename_pattern = StringField('File name pattern')
    data_format = SelectField('Data field', choices=[
        source.DirectorySource.DATA_FORMAT_JSON,
        source.DirectorySource.DATA_FORMAT_CSV,
        source.DirectorySource.DATA_FORMAT_AVRO,
        source.DirectorySource.DATA_FORMAT_LOG,
    ])
    # todo несколько вариантов дальнейшего запроса в зависимости от дата формата
    csv_format_type = SelectField('Delimited format type', choices=[
        source.DirectorySource.CONFIG_CSV_TYPE_CUSTOM,
        source.DirectorySource.CONFIG_CSV_TYPE_DEFAULT,
    ])
    custom_delimiter_character = StringField('Customer delimiter character')
    override_filed_names = StringField('Change field names')


class EditDirectory(Directory):
    pass


forms = {
    source.TYPE_INFLUX: Influx,
    source.TYPE_KAFKA: Kafka,
    source.TYPE_MONGO: Mongo,
    source.TYPE_MYSQL: MySQL,
    source.TYPE_POSTGRES: Postgres,
    source.TYPE_ELASTIC: Elastic,
    source.TYPE_SPLUNK: Splunk,
    source.TYPE_DIRECTORY: Directory,
}

edit_forms = {
    source.TYPE_INFLUX: EditInflux,
    source.TYPE_KAFKA: EditKafka,
    source.TYPE_MONGO: EditMongo,
    source.TYPE_MYSQL: EditMySQL,
    source.TYPE_POSTGRES: EditPostgres,
    source.TYPE_ELASTIC: EditElastic,
    source.TYPE_SPLUNK: EditSplunk,
    source.TYPE_DIRECTORY: EditDirectory,
}


class FormType(Enum):
    CREATE = 1
    EDIT = 2


def get_form(source_type: str, form_type: FormType) -> Type[SourceForm]:
    if form_type == FormType.CREATE:
        return forms[source_type]
    return edit_forms[source_type]
