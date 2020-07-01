from agent.cli import source as source_cli
from agent import cli

# help('modules')
#
# cli.destination()
# source_cli.create()
# pipeline_cli.create()
# cli.update()

import requests
sage_url = 'http://localhost:8888'
user_token = '<JWT token>'
body = {"clientId": "test-token-app", "groups": ["sage"], "permissions": ["search"]}

resp = requests.post("%s/cc/api/tokens/" % sage_url, json=body, verify=False, headers={'Authorization': 'Bearer %s' % user_token})
print(resp.content.decode('utf-8'))
