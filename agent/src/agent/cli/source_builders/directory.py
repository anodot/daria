import click

from .schemaless import SchemalessSource


class DirectorySource(SchemalessSource):
    CONFIG_DIR = 'conf.spoolDir'
    CONFIG_FILE_PATTERN = 'conf.filePattern'
    CONFIG_SPOOLING_PERIOD = 'conf.spoolingPeriod'

    TEST_PIPELINE_FILENAME = 'test_directory_ksdjfjk21'

    VALIDATION_SCHEMA_FILE_NAME = 'directory.json'

    def prompt(self, default_config, advanced=False):
        self.source.config[self.CONFIG_DIR] = \
            click.prompt('Directory path', type=click.Path(file_okay=False),
                         default=default_config.get(self.CONFIG_DIR))
        self.source.config[self.CONFIG_FILE_PATTERN] = \
            click.prompt('File name pattern', type=click.STRING,
                         default=default_config.get(self.CONFIG_FILE_PATTERN, '*'))
        self.prompt_data_format(default_config)
        self.prompt_batch_size(default_config)
        return self.source.config

    def validate(self):
        self.validate_json()
        self.validate_connection()

    def prompt_csv(self, default_config):
        self.prompt_csv_type(default_config)
        default_use_header = default_config.get(self.CONFIG_CSV_HEADER_LINE, self.CONFIG_CSV_HEADER_LINE_WITH_HEADER)
        if click.confirm('Use header line?',
                         default=True if default_use_header == self.CONFIG_CSV_HEADER_LINE_WITH_HEADER else False):
            self.source.config[self.CONFIG_CSV_HEADER_LINE] = self.CONFIG_CSV_HEADER_LINE_WITH_HEADER
        else:
            self.source.config[self.CONFIG_CSV_HEADER_LINE] = self.CONFIG_CSV_HEADER_LINE_NO_HEADER
            self.change_field_names(default_config)
