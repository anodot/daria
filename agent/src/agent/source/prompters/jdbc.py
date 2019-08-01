import click


class PromptJDBC:

    def prompt(self, default_config, advanced=False):
        config = dict()
        config['connection_string'] = click.prompt('Connection string',
                                                   type=click.STRING,
                                                   default=default_config.get('connection_string'))
        config['hikariConfigBean.username'] = click.prompt('Username',
                                                           type=click.STRING,
                                                           default=default_config.get('hikariConfigBean.username', ''))
        config['hikariConfigBean.password'] = click.prompt('Password',
                                                           type=click.STRING,
                                                           default=default_config.get('hikariConfigBean.password', ''))

        config['query_interval'] = click.prompt('Query interval (seconds)', type=click.STRING,
                                      default=default_config.get('query_interval', '10'))

        if config['hikariConfigBean.password'] == '':
            config['hikariConfigBean.useCredentials'] = False
        return config
