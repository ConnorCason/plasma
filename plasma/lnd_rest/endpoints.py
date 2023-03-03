import base64, codecs, json, os, requests

from plasma.db.db_utils import get_alias

MACAROON = codecs.encode(open('/home/umbrel/umbrel/app-data/lightning/data/lnd/data/chain/bitcoin/mainnet/admin.macaroon'))
REST_HOST = 'umbrel.local:8080'
TLS_PATH = '/home/umbrel/umbrel/app-data/lightning/data/lnd/tls.cert'
# MACAROON = os.environ.get('LND_MACAROON_BINARY')
# REST_HOST = os.environ.get('LND_REST_HOST')
# TLS_PATH = os.environ.get('LND_TLS_PATH')

# Return models?
def send_request(_type, endpoint, data=None, stream=None):
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
    elif _type == 'stream':
        res = requests.post(
            url, 
            headers=headers, 
            stream=stream,
            verify=TLS_PATH
        )
        return res
    
    return res.json()

# Channels
def get_channels():
    return send_request('GET', 'v1/channels')['channels']

def get_channel_info(channel_id):
    return send_request('GET', f'v1/graph/edge/{channel_id}')

def update_channel_policy(chan_point, base_fee, ppm_fee):
    chan_point_sep = chan_point.split(':')
    lnd_ChannelPoint = {
        'funding_txid_str': chan_point_sep[0],
        'output_index': int(chan_point_sep[1])
    }
    _data = {
        'chan_point': lnd_ChannelPoint,
        'base_fee_msat': base_fee,
        'fee_rate_ppm': ppm_fee,
        'time_lock_delta': 144
    }
    return send_request(
        'POST', 
        'v1/chanpolicy', 
        data=_data
    )



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
        'outgoing_chan_id': outgoing_chan_id,
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
    return send_request('GET', 'v2/router/htlcevents', stream=True)


# Payments 

def add_invoice(sat_amt):
    _data = {
        'expiry': 300,
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

# def decrypt_str(_str):
#     return base64.