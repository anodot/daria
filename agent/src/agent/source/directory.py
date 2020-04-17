import click

from agent.tools import infinite_retry
from .schemaless import SchemalessSource


class DirectorySource(SchemalessSource):
    CONFIG_DIR = 'conf.spoolDir'
    CONFIG_FILE_PATTERN = 'conf.filePattern'
    CONFIG_SPOOLING_PERIOD = 'conf.spoolingPeriod'

    TEST_PIPELINE_NAME = 'test_directory_ksdjfjk21'

    VALIDATION_SCHEMA_FILE_NAME = 'directory.json'

    def prompt(self, default_config, advanced=False):
        self.config[self.CONFIG_DIR] = click.prompt('Directory path',
                                                    type=click.Path(dir_okay=True, file_okay=False),
                                                    default=default_config.get(self.CONFIG_DIR))
        self.config[self.CONFIG_FILE_PATTERN] = click.prompt('File name pattern',
                                                             type=click.STRING,
                                                             default=default_config.get(self.CONFIG_FILE_PATTERN, '*'))

        self.prompt_data_format(default_config)
        self.prompt_batch_size(default_config)
        return self.config

    def validate(self):
        self.validate_json()
        self.validate_connection()
