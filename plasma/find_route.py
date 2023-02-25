import json
import math
import networkx as nx
from tabulate import tabulate
import time
import sys

import plasma.lnd_rest.endpoints as e
import plasma.db.db_reader as reader
import plasma.db.db_utils as d_utils

replace_dict = {
    "'": '"',
    'True': '"True"',
    'False': '"False"'
}


def find_route(dest_pubkey, sat_amt):
    ln_g = build_lightning_multidigraph(sat_amt)
    print(f'Trying to route {sat_amt}sat to {dest_pubkey}')
    
    path = nx.shortest_path(
        ln_g, 
        '0323aac79814817b023ce6e4eac13c961df213e773e901f74fa4c9477f22e0f304',
        dest_pubkey,
        weight='cost'
    )
    length = nx.shortest_path_length(
        ln_g,
        '0323aac79814817b023ce6e4eac13c961df213e773e901f74fa4c9477f22e0f304',
        dest_pubkey,
        weight='cost'
    )

    # print(path)
    path = [d_utils.get_alias(pkey) for pkey in path]
    print(path)
    print(length)


    return path
        


def build_lightning_multidigraph(sat_amt):
    s = time.time()
    print(f'Building LN Multidigraph for a {sat_amt}sat payment...')
    all_channels = reader.get_network_channels()
    num_channels = all_channels.shape[0]
    G = nx.MultiDiGraph()

    for index, row in all_channels.iterrows():
        if ((index+1) % 10000) == 0:
            print(f'{index+1}/{num_channels} edges constructed')
        add_directed_edge(G, row['channel_id'], row['node1_pub'], row['node2_pub'],
            row['node1_policy'], sat_amt, index)
        add_directed_edge(
            G, row['channel_id'], row['node2_pub'], row['node1_pub'],
            row['node2_policy'], sat_amt, index)

    print(f'Generated {G} in {int(time.time()-s)} seconds')
    return G
        

def add_directed_edge(G, chan_id, source_pub, dest_pub, source_policy, sat_amt, index):

    if isinstance(source_policy, float):
        # print(f'Channel {index+1}: no outbound policy')
        return 0
    elif isinstance(source_policy, str):
        for replacement in replace_dict:
            source_policy = source_policy.replace(
                replacement, 
                replace_dict[replacement]
            )
        p_dict = json.loads(source_policy)
        fees = [int(p_dict['fee_base_msat']), int(p_dict['fee_rate_milli_msat'])]
        cost = int(fees[0]/(10**3)) + (int(fees[1])/(10**6) * sat_amt)
        # print(f'Channel {index+1}: F = {fees[0]}msat + {fees[1]}ppm; C = {cost}')
        G.add_edge(source_pub, dest_pub, chan_id=chan_id, cost=cost
        )
        return 1
    else:
        print('WTF???')
        return 0
