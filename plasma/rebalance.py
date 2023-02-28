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

MY_PUBKEY = os.environ.get('MY_PUBKEY')
CUSTODIAL_HOPS = 2

replace_dict = {
    "'": '"',
    'True': '"True"',
    'False': '"False"'
}

def find_shortest_path(source_pubkey, dest_pubkey, 
    sat_amt, ln_g=None):
    if not ln_g:
        ln_g = build_lightning_multidigraph(sat_amt)
        print(f'Finding shortest path for:\n~{sat_amt} sat\n-from: {source_pubkey}\n+to: {dest_pubkey}\n')
        # Remove direct connection with dest peer
        ln_g.remove_edge(MY_PUBKEY, dest_pubkey)
    
    path = nx.shortest_path(ln_g, source_pubkey,
        dest_pubkey)
    
    path.append(MY_PUBKEY)
    
    chs = []
    for i in range(len(path)-1):
        ed = ln_g.get_edge_data(path[i], path[i+1])
        chs.append(ed)

    alias_path = [d_utils.get_alias(pkey) for pkey in path]
    c_buff = '                         '
    tc = 0
    print(f'Outbound from            Cost')
    for i, alias in enumerate(alias_path[:-1]):
        curr_buff = c_buff[:len(c_buff) - len(alias)]
        connecting_channel_cost_sat = round(chs[i][0]['cost'] * .001, 2)
        ccc_str = f'{connecting_channel_cost_sat} sat' if connecting_channel_cost_sat != 0 else 'Free   '
        base = chs[i][0]['base']
        ppm = chs[i][0]['ppm']
        print(f'{alias}{curr_buff}{ccc_str} ({base}msat, {ppm}ppm)')
        tc += connecting_channel_cost_sat
    lh_costs_str = f'{round(chs[-1][0]["cost"] * .001, 2)} sat'
    lh_policy_str = f'({chs[-1][0]["base"]}msat, {chs[-1][0]["ppm"]}ppm)'
    print(f'{alias_path[-1]}')
    print(f'{c_buff}{tc} sat Total')
    
    sys.exit(0)
    return (int(chs[0][0]['chan_id']), path, ln_g)


def find_cheapest_path(source_pubkey, dest_pubkey, sat_amt, 
                        ln_g, max_fee=None, max_hops=6):
    
    print(f'Finding cheapest path for:\n~{sat_amt} sat\n-from: {d_utils.get_alias(source_pubkey)}\n+to: {d_utils.get_alias(dest_pubkey)}\n')

    # Return list of pubkeys
    path = nx.dijkstra_path(ln_g, source_pubkey,
        dest_pubkey, weight='cost')
    
    if len(path) > (CUSTODIAL_HOPS + max_hops):
        print('Doing graph algorithm magic...')
    while len(path) > (CUSTODIAL_HOPS + max_hops):
        # print(f'Removing edge {d_utils.get_alias(path[max_noncustodial_hops-1])} ---> {d_utils.get_alias(path[max_noncustodial_hops])}')
        ln_g.remove_edge(path[max_hops-1], path[max_hops])
        path = nx.dijkstra_path(ln_g, source_pubkey,
            dest_pubkey, weight='cost')
    # print(f'path returned by networkx: {path}')

    # Create full cycle path regardless
    if path[0] != MY_PUBKEY:
        path.insert(0, MY_PUBKEY)
    if path[-1] != MY_PUBKEY:
        path.append(MY_PUBKEY)

    # print(f'adjusted path: {path}')
    # print(f'channels: {chs}')
    cycle_detected = MY_PUBKEY in path[1:-1]
    
    return (path, ln_g)
        

def build_lightning_multidigraph(sat_amt):
    s = time.time()
    print(f'Building LN Multidigraph for a {sat_amt}sat payment...')
    all_channels = reader.get_network_channels()
    G = nx.MultiDiGraph()

    for index, row in all_channels.iterrows():
        # if ((index+1) % 10000) == 0:
        #     print(f'{index+1}/{num_channels} edges constructed')
        
        if int(row['capacity']) >= int(sat_amt * 1.5):
            # Add edge from 1 to 2 with outbound policy for 1 as weight
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
        cost_msat = fees[0] + (fees[1] * .001 * sat_amt) if source_pub != MY_PUBKEY else 0
        G.add_edge(
            source_pub, 
            dest_pub, 
            chan_id=chan_id,
            chan_point=chan_point, 
            capacity=capacity,
            base=fees[0],
            ppm=fees[1],
            cost=cost_msat,
            policy_holder=source_pub
        )
        return 1
    else:
        print('WTF???')
        return 0


def rebalance(source_pubkey, dest_pubkey, sat_amt, max_fee=None, 
    max_hops=None, method=None, favorate_paths=None):
    
    graph = build_lightning_multidigraph(sat_amt)

    # If source is specified, remove edge from source to my node to
    # make sure I can't recieve through the same channel I am tryng to send through
    if source_pubkey != MY_PUBKEY:
        graph.remove_edge(source_pubkey, MY_PUBKEY, policy_holder=source_pubkey)

    # If dest is specified, remove edge from my node to dest to
    # make sure I can't send through the same channel I am tryng to recieve through
    if dest_pubkey != MY_PUBKEY:
        graph.remove_edge(MY_PUBKEY, dest_pubkey, policy_holder=MY_PUBKEY)
    

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
        # print(path_info[0], path_info[1])

        past_max_fee = print_route_summary(path_info[0], path_info[1], max_fee)
        if past_max_fee:
            break

        invoice = e.add_invoice(sat_amt)
        payment_hash = invoice['r_hash']
        lnurl = invoice['payment_request']
        payment_address = invoice['payment_addr']
        # print('Payment invoice...')
        # print(json.dumps(invoice, indent=4))
        
        out_chan_id = str(d_utils.get_chan_id_of_peers(
                path_info[0][0],
                path_info[0][1]
            ))
        route = e.build_route(sat_amt, out_chan_id, path_info[0][1:], payment_address)
        if build_route_failed(route, path_info, graph):
            continue
        # print(json.dumps(route, indent=4))

        resp = e.pay_to_route_synchronous(payment_hash, route['route'])
        pe = resp['payment_error']
        # print(json.dumps(resp, indent=2))

        if pe:
            # print(pe)
            hop_error_index = int(pe[-1:])
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
        print(message)
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
# Returns True if route exceeds max fee
# Returns False otherwise
def print_route_summary(path, graph, max_fee):

    chs = []
    for i in range(len(path)-1):
        ed = graph.get_edge_data(path[i], path[i+1])
        chs.append(ed[0])

    alias_path = [d_utils.get_alias(pkey) for pkey in path]
    # print(alias_path)
    c_buff = '                         '
    tc = 0
    for i, alias in enumerate(alias_path[:-1]):
        curr_buff = c_buff[:len(c_buff) - len(alias)]
        connecting_channel_cost_sat = round(chs[i]['cost'] * .001, 2)
        ccc_str = f'{connecting_channel_cost_sat} sat' if connecting_channel_cost_sat != 0 else 'Free   '
        base = chs[i]['base']
        ppm = chs[i]['ppm']
        print(f'{alias}{curr_buff}{ccc_str} ({base}msat, {ppm}ppm)')
        tc += connecting_channel_cost_sat
    print(f'AlphaStreet              {tc} sat Total\n')

    if max_fee and (tc > max_fee):
        print(f'No routes left below {max_fee} sats')
        return True        
    
    return False