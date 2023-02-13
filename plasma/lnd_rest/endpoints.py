import codecs, json, os, requests


REST_HOST = os.environ.get('LND_REST_HOST')
MACAROON_PATH = os.environ.get('LND_MACAROON_PATH')
TLS_PATH = os.environ.get('LND_TLS_PATH')

# Return models 
def send_request(type, endpoint, return_raw=False):
    url = f'https://{REST_HOST}/v1/{endpoint}'
    macaroon = codecs.encode(open(MACAROON_PATH, 'rb').read(), 'hex')
    headers = {'Grpc-Metadata-macaroon': macaroon}
    response = None
    if type == 'GET':
        response = requests.get(url, headers=headers, verify=TLS_PATH)
    elif type == 'POST':
        response = requests.post(url, headers=headers, verify=TLS_PATH)
    
    formatted = json.dumps(response.json(), indent=2)
    print(formatted)
    return formatted

def get_info():
    return send_request('GET', 'getinfo')

def get_forwarding_history():
    return send_request('POST', 'switch')