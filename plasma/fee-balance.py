import plasma.db.db_reader as reader
import plasma.db.db_writer as writer
import plasma.db.db_utils as utils

NODES = {
    # nodl-lnd-s007-001
    '02691fbf5f161d13640d2c8bc1fcb47a601badfaf5b82e892d75376e3bf540a590': {
        'type': 'standard',
        'multiplier': 1
    },

    # 1.ln.aantonop.com
    '0237fefbe8626bf888de0cad8c73630e32746a22a2c4faa91c1d9877a3826e1174': {
        'type': 'standard',
        'multiplier': 1 
    },

    '039f6f74de35652c3d804cd873f14cc858e26beb3fda9d14363bae40d94bc72fde': 'source', # Crypto-RiS
}
STANDARD_FEE_STRUCTURE = {
    .10: (0, 100),
    .25: (0, 50),
    .50: (0, 20),
    .75: (0, 10),
    .90: (0, 1)
}
SOURCE_FEE_STRUCTURE = {
    .10: (0, 50),
    .25: (0, 25),
    .50: (0, 10),
    .75: (0, 5),
    .90: (0, 1)
}
SINK_FEE_STRUCTURE = {
    .10: (10000, 500),
    .25: (5000, 250),
    .50: (2500, 100),
    .75: (1000, 50),
    .90: (0, 25)
}


def fee_balance():
    writer.update_dbs(rebuild_network_topology=False)
    channels = reader.get_local_channels()
    for index, channel in channels.iterrows():
        peer = channel['remote_pubkey']
        if peer in NODES.keys():
            peer_type = NODES[peer]['type']
            peer_fee_multiplier = NODES[peer]['multiplier']
            fee_structure = choose_fee_structure(peer_type)
            chan_id = channel['chan_id']
            chan_cap = channel['capacity']
            chan_balance = channel['local_balance']
            chan_ratio = round((chan_balance/chan_cap * 100), 2)
            print(f'{utils.get_alias(peer)}:')
            print(f'\tBalance: {chan_balance} sat ({chan_ratio}% local)')
            print(f'\tCurrent fees: ')

def choose_fee_structure(peer_type):
    if peer_type == 'standard':
        return STANDARD_FEE_STRUCTURE
    elif peer_type == 'source':
        return SOURCE_FEE_STRUCTURE
    elif peer_type == 'sink':
        return SINK_FEE_STRUCTURE



if __name__ == '__main__':
    fee_balance()