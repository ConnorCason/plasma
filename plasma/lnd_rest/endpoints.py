import json, os, requests

MACAROON = os.environ.get('LND_MACAROON_BINARY')
REST_HOST = os.environ.get('LND_REST_HOST')
TLS_PATH = os.environ.get('LND_TLS_PATH')

# Return models?
def send_request(_type, endpoint, data=None):
    url = f'https://{REST_HOST}/{endpoint}'
    headers = {'Grpc-Metadata-macaroon': MACAROON}
    res = None
    if _type == 'GET':
        res = requests.get(url, headers=headers, verify=TLS_PATH)
    elif _type == 'POST':
        res = requests.post(
            url, 
            headers=headers, 
            data=json.dumps(data),
            verify=TLS_PATH
        )
    
    return res.json()

# Channels
def get_channels():
    return send_request('GET', 'v1/channels')['channels']

def get_channel_info(channel_id):
    return send_request('GET', f'v1/graph/edge/{channel_id}')



# Node
def get_info():
    return send_request('GET', 'v1/getinfo')

# Routing
def get_forwarding_history():
    _data = {
        'num_max_events': 10000
    }
    return send_request(
        'POST', 
        'v1/switch',
        data=_data
    )['forwarding_events']

def get_routes(dest_pubkey, sat_amt):
    return send_request('GET', f'v1/graph/routes/{dest_pubkey}/{sat_amt}')['routes']


# Network Topology
def get_graph():
    return send_request('GET', 'v1/graph')


# Exploratory   
def get_htlc_events():
    return send_request('GET', 'v2/router/htlcevents')