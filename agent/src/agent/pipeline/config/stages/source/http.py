from agent.pipeline.config.stages.base import Stage

# todo move? this stage is not used yet but I keep it for future
BASIC_AUTH = 'BASIC'


class Http(Stage):
    def get_config(self) -> dict:
        return {
            'conf.resourceUrl': self.pipeline.source.config['url'],
            **self._get_authentication(),
        }

    def _get_authentication(self) -> dict:
        auth = {}
        if self.pipeline.source.authentication:
            auth_type = self.pipeline.source.authentication['type'].upper()
            auth['conf.client.authType'] = auth_type
            if auth_type == BASIC_AUTH:
                auth['conf.client.basicAuth.username'] = self.pipeline.source.authentication['username']
                auth['conf.client.basicAuth.password'] = self.pipeline.source.authentication['password']
            else:
                raise Exception(f'Authentication type `{auth_type}` is not supported')
        return auth
