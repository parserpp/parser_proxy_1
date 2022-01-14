import requests
import json
import os

def run():
    payload = json.dumps({"event_type": "webhook-1"})
    header = {'Authorization': f'token '+os.getenv('GITHUB_TOKEN', ""), "Accept": "application/vnd.github.everest-preview+json"}
    response_decoded_json = requests.post(
            f'https://api.github.com/repos/parserpp/parser_proxy_poll/dispatches',
            data=payload, headers=header)
run()
