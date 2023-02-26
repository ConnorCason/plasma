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


def find_route(source_pubkey, dest_pubkey, sat_amt, ln_g):
    if not ln_g:
        ln_g = build_lightning_multidigraph(sat_amt)
        print(f'Finding route for:\n~{sat_amt} sat\n-from: {source_pubkey} \
        \n+to: {dest_pubkey}\n')

    path = nx.dijkstra_path(ln_g, source_pubkey,
        dest_pubkey, weight='cost')

    alias_path = [d_utils.get_alias(pkey) for pkey in path]
    # print(alias_path)
    
    chs = []
    for i in range(len(path)-1):
        ed = ln_g.get_edge_data(path[i], path[i+1])
        chs.append(ed)
    
    print(f'Attempting route (alias / cost):')
    c_buff = '                 '
    tc = 0
    for alias in alias_path:
        curr_buff = c_buff[:len(c_buff) - len(alias)]
        connecting_channel_cost = int(chs[i][0]['cost'])
        print(f'{alias}{curr_buff}{connecting_channel_cost}')
        tc += connecting_channel_cost
    print(f'{c_buff}{tc}')


    # summary = ''
    # for i in range(len(chs)):
    #     summary += alias_path[i]
    #     connecting_channel_cost = int(chs[i][0]['cost'])
    #     summary += f' --{connecting_channel_cost}sat--> '
    # summary += alias_path[len(alias_path)-1]
    # print(f'Attempting route:\n{summary}')
    # cps = [ch[0]['chan_point'] for ch in chs]
    # print(f'chan points: {cps}')

    # print(path)
    # for k in path:
    #     print(len(k))
    return (int(chs[0][0]['chan_id']), path, ln_g)
        

def build_lightning_multidigraph(sat_amt):
    s = time.time()
    print(f'Building LN Multidigraph for a {sat_amt}sat payment...')
    all_channels = reader.get_network_channels()
    num_channels = all_channels.shape[0]
    G = nx.MultiDiGraph()

    for index, row in all_channels.iterrows():
        # if ((index+1) % 10000) == 0:
        #     print(f'{index+1}/{num_channels} edges constructed')
        
        if int(row['capacity']) >= int(sat_amt * 1.5):
            add_directed_edge(G, row['channel_id'], row['chan_point'], 
                row['node1_pub'], row['node2_pub'],row['node1_policy'],
                row['capacity'], sat_amt, index)
            add_directed_edge(G, row['channel_id'], row['chan_point'],
                row['node2_pub'], row['node1_pub'], row['node2_policy'], 
                row['capacity'], sat_amt, index)

    print(f'Generated {G} in {int(time.time()-s)} seconds\n')
    return G
        

def add_directed_edge(G, chan_id, chan_point, source_pub, dest_pub, 
    source_policy, capacity, sat_amt, index):

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
        G.add_edge(
            source_pub, 
            dest_pub, 
            chan_id=chan_id,
            chan_point=chan_point, 
            capacity=capacity,
            cost=cost)
        return 1
    else:
        print('WTF???')
        return 0
