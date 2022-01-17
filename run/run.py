import json
import os
import ssl
import sys
import requests
import urllib3
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# sys.path.append('../')
# ssl._create_default_https_context = ssl._create_unverified_context


def run():
    payload = json.dumps({"event_type": "webhook-1"})
    header = {'Authorization': f'token '+os.getenv('GITHUB_TOKEN', ""), "Accept": "application/vnd.github.everest-preview+json"}
    response_decoded_json = requests.post(
            f'https://api.github.com/repos/parserpp/parser_proxy_poll/dispatches',
            data=payload, headers=header,verify=False)
    print(response_decoded_json.text)
run()
