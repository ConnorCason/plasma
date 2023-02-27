import base64, json, os, requests

from plasma.db.db_utils import get_alias

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

def build_route(sat_amt, outgoing_chan_id, hop_pubkeys, payment_address):
    
    _data = {
        'amt_msat': str((sat_amt) * (10**3)),
        'final_cltv_delta': 144,
        'outgoing_chan_id': str(outgoing_chan_id),
        'hop_pubkeys': [encrypt_str(pub) for pub in hop_pubkeys],
        'payment_addr': payment_address
    }
    return send_request(
        'POST', 
        'v2/router/route', 
        data=_data
    )


def estimate_fee(dest_pubkey, sat_amt):
    _data = {
        'dest': encrypt_str(dest_pubkey),
        'amt_sat': sat_amt
    }
    return send_request(
        'POST',
        'v2/router/route/estimatefee',
        data=_data
    )

# Network Topology
def get_graph():
    return send_request('GET', 'v1/graph')


# Exploratory   
def get_htlc_events():
    return send_request('GET', 'v2/router/htlcevents')


# Payments 

def add_invoice(sat_amt):
    _data = {
        'expiry': 120,
        'value': sat_amt
    }
    return send_request(
        'POST',
        'v1/invoices',
        data=_data
    )

def pay_to_route_synchronous(payment_hash, _route):
    _data = {
        'payment_hash': payment_hash,
        'route': _route
    }
    return send_request(
        'POST',
        'v1/channels/transactions/route',
        data=_data
    )




def encrypt_str(_str):
    return base64.b64encode(bytes.fromhex(_str)).decode()