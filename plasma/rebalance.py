import os
import json
import math
import networkx as nx
from tabulate import tabulate
import time
import sys

import plasma.lnd_rest.endpoints as e
import plasma.db.db_reader as reader
import plasma.db.db_utils as d_utils

MY_PUBKEY = '0323aac79814817b023ce6e4eac13c961df213e773e901f74fa4c9477f22e0f304'
CHANNEL_CAP_MULTIPLIER = 2

replace_dict = {
    "'": '"',
    'True': '"True"',
    'False': '"False"'
}

def find_shortest_path(source_pubkey, dest_pubkey, sat_amt, 
                       ln_g, max_fee=None, max_hops=None):
    # Return list of pubkeys
    path = nx.shortest_path(ln_g, source_pubkey, dest_pubkey) 

    if path[0] != MY_PUBKEY:
        path.insert(0, MY_PUBKEY)
    if path[-1] != MY_PUBKEY:
        path.append(MY_PUBKEY)

    return (path, ln_g)


def find_cheapest_path(source_pubkey, dest_pubkey, sat_amt, 
                        ln_g, max_fee=None, max_hops=None):

    # Return list of pubkeys
    path = nx.dijkstra_path(ln_g, source_pubkey,
        dest_pubkey, weight='cost')

    if max_hops:
        if len(path) >= (max_hops):
            print('Doing graph algorithm magic...')
        while len(path) > (max_hops):
            # print('This path is too long:')
            # for i in path:
            #     print(d_utils.get_alias(i))
            # print(f'Removing edge {d_utils.get_alias(path[max_hops-1])} ---> {d_utils.get_alias(path[max_hops])}')
            ln_g.remove_edge(path[max_hops-1], path[max_hops])
            path = nx.dijkstra_path(ln_g, source_pubkey,
                dest_pubkey, weight='cost')
        

    if path[0] != MY_PUBKEY:
        path.insert(0, MY_PUBKEY)
    if path[-1] != MY_PUBKEY:
        path.append(MY_PUBKEY)

    return (path, ln_g)
        

def build_lightning_multidigraph(sat_amt):
    s = time.time()
    print(f'Building LN Multidigraph for a {sat_amt}sat payment...')
    all_channels = reader.get_network_channels()
    G = nx.MultiDiGraph()

    for index, row in all_channels.iterrows():
        if int(row['capacity']) >= int(sat_amt * CHANNEL_CAP_MULTIPLIER):
            add_directed_edge(G, row['channel_id'], row['chan_point'], 
                row['node1_pub'], row['node2_pub'],row['node1_policy'],
                row['capacity'], sat_amt)
            add_directed_edge(G, row['channel_id'], row['chan_point'],
                row['node2_pub'], row['node1_pub'], row['node2_policy'], 
                row['capacity'], sat_amt)
    print(f'Generated {G} in {int(time.time()-s)} seconds\n')
    return G
        

def add_directed_edge(G, chan_id, chan_point, source_pub, dest_pub, 
    source_policy, capacity, sat_amt):

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
        cost_msat = fees[0] + (fees[1] * .001 * sat_amt) if source_pub != MY_PUBKEY else 0
        G.add_edge(
            source_pub, 
            dest_pub,
            chan_id=chan_id,
            # chan_point=chan_point, 
            capacity=capacity,
            base=fees[0],
            ppm=fees[1],
            cost=cost_msat
        )
        return 1
    else:
        print('WTF???')
        return 0


def rebalance(source_pubkey, dest_pubkey, sat_amt, max_fee=None, 
    max_hops=None, method=None, favorate_paths=None):
    
    graph = build_lightning_multidigraph(sat_amt)
    # 
    if source_pubkey != MY_PUBKEY:
        graph.remove_edge(source_pubkey, MY_PUBKEY)
    if dest_pubkey != MY_PUBKEY:
        graph.remove_edge(MY_PUBKEY, dest_pubkey)
    print(f'Finding cheapest path for:\n~{sat_amt} sat\n-from: {d_utils.get_alias(source_pubkey)}\n+to: {d_utils.get_alias(dest_pubkey)}\n')
    
    sent = False
    attempt_number = 0
    while not sent:
        attempt_number += 1
        print(f'Attempt #{attempt_number}')

        if favorate_paths:
            print('Trying favorite...')
            path_info = (
                favorate_paths.pop(0).split(','), 
                graph
            )
        elif method == 'cheapest':
            path_info = find_cheapest_path(source_pubkey, dest_pubkey, 
                sat_amt, graph, max_fee, max_hops)
        else:
            path_info = find_shortest_path(source_pubkey, dest_pubkey, 
                sat_amt, graph, max_fee, max_hops) 
        graph = path_info[1]

        route_return_code = print_route_summary(path_info[0], path_info[1], max_fee)
        if route_return_code == 1 and method == 'shortest':

            continue
        elif route_return_code == 1:
            break
            

        invoice = e.add_invoice(sat_amt)
        payment_hash = invoice['r_hash']
        lnurl = invoice['payment_request']
        payment_address = invoice['payment_addr']
        
        out_chan_id = str(d_utils.get_chan_id_of_peers(
                path_info[0][0],
                path_info[0][1]
            ))
        route = e.build_route(sat_amt, out_chan_id, path_info[0][1:], payment_address)
        if build_route_failed(route, path_info, graph):
            continue

        resp = e.pay_to_route_synchronous(payment_hash, route['route'])
        pe = resp['payment_error']

        if pe:
            # print(pe)
            try:
                hop_error_index = int(pe[-1:])
            except ValueError:
                print('cant cast, see below')
                print(pe)
            _source_pubkey = route['route']['hops'][hop_error_index-1]['pub_key']
            _dest_pubkey = route['route']['hops'][hop_error_index]['pub_key']
            s_alias = d_utils.get_alias(_source_pubkey)
            d_alias = d_utils.get_alias(_dest_pubkey)
            print(f'{s_alias} ---> {d_alias}: TCF, removing...\n')
            graph.remove_edge(_source_pubkey, _dest_pubkey)
        else:
            print('POSSIBLE SUCCESS, info:')
            print(f'Routing information:\n{path_info[0], path_info[1]}')
            print(f'Invoice:\n{json.dumps(invoice, indent=4)}')
            print(f'Route:\n{json.dumps(route, indent=4)}')
            print(f'Payment response:\n{json.dumps(resp, indent=4)}')
            with open('verified_paths.txt', 'a') as pathfile:
                pathfile.write(f'\n{d_utils.get_alias(dest_pubkey)}\n')
                pathfile.write(','.join(path_info[1]) + '\n')
            sent = True
        
        
def build_route_failed(route, path_info, graph):
    if list(route.keys())[0] == 'code':
        message = route['message']
        # print(message)
        if 'no matching' in message:
            _source_pubkey = message[-67:-1]
            _dest_pubkey = path_info[0][
                path_info[0].index(_source_pubkey) + 1
            ]
            print(f'{d_utils.get_alias(_source_pubkey)} ---> {d_utils.get_alias(_dest_pubkey)}: CCF, removing...\n')
            graph.remove_edge(_source_pubkey, _dest_pubkey)
            return True
        else:
            print('PANIK')
            print(message)
            import sys
            sys.exit(0)
    return False


# Prints route summary
# Returns 0 if no issues found
# Returns 1 if route exceeds max fee (or favorited route has insufficient capacity)
def print_route_summary(path, graph, max_fee):

    alias_path = [d_utils.get_alias(pkey) for pkey in path]

    chs = []
    for i in range(len(path)-1):
        ed = graph.get_edge_data(path[i], path[i+1])
        chs.append(ed[0])
        
    
    # print(alias_path)
    c_buff = '                         '
    tc = 0
    max_cost_peer = (None, 0)
    for i, alias in enumerate(alias_path[:-1]):
        curr_buff = c_buff[:len(c_buff) - len(alias)]
        connecting_channel_cost_sat = round(chs[i]['cost'] * .001, 2)
        ccc_str = f'{connecting_channel_cost_sat} sat' if connecting_channel_cost_sat != 0 else 'Free   '
        base = chs[i]['base']
        ppm = chs[i]['ppm']
        print(f'{alias}{curr_buff}{ccc_str} ({base}msat, {ppm}ppm)')
        tc += connecting_channel_cost_sat
        if connecting_channel_cost_sat > max_cost_peer[1]:
            max_cost_peer = (i, connecting_channel_cost_sat)
    print(f'AlphaStreet              {round(tc, 2)} sat Total\n')

    if max_fee and (tc > max_fee):
        print(f'{alias_path[max_cost_peer[0]]} --> {alias_path[max_cost_peer[0]+1]}: too expensive, removing...')
        graph.remove_edge(path[max_cost_peer[0]], path[max_cost_peer[0]+1])
        time.sleep(5)
        return 1
    
    return 0