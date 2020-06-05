class Proxy:
    # todo test how None password works
    def __init__(self, uri: str, username: str = '', password: str = ''):
        self.uri = uri
        self.username = username
        self.password = password
