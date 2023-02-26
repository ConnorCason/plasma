import plasma.lnd_rest.endpoints as e
import plasma.metrics.routing as r
import plasma.db.db_reader as reader
import plasma.db.db_writer as writer
import plasma.db.db_utils as utils
import plasma.find_route as router

import json
import time

from tabulate import tabulate

if __name__ == "__main__":
    writer.update_dbs(rebuild_network_topology=False)

    _from = '0323aac79814817b023ce6e4eac13c961df213e773e901f74fa4c9477f22e0f304'
    _to = '03df3f0a2fd6bea5429a596461ce784c922b2981ada1af89cfefcd9ccfb16c16a7'
    sat_amt = 100
    max_hops = 5

    sent = False
    graph = None
    attempt_number = 1

    while not sent:
        print(f'Attempt #{attempt_number}')
        routing_info = router.find_route(
            _from, _to, sat_amt, graph
        )
        graph = routing_info[2]
        # print(routing_info[0], routing_info[1])

        invoice = e.add_invoice(sat_amt)
        payment_hash = invoice['r_hash']
        lnurl = invoice['payment_request']
        payment_address = invoice['payment_addr']

        # print('Payment invoice...')
        # print(json.dumps(invoice, indent=4))

        route = e.build_route(sat_amt, routing_info[0], routing_info[1], payment_address)
        if list(route.keys())[0] == 'code':
            message = route['message']
            if 'no matching' in message:
                source_pubkey = message[-67:-1]
                dest_pubkey = routing_info[1][
                    routing_info[1].index(source_pubkey) + 1
                ]
                print(f'{utils.get_alias(source_pubkey)} ---> {utils.get_alias(dest_pubkey)}: CCF, removing...\n')
                graph.remove_edge(source_pubkey, dest_pubkey)
                attempt_number += 1
                time.sleep(1)
                continue
            else:
                print('PANIK')
                import sys
                sys.exit(0)
        
        # print(json.dumps(route, indent=4))

        resp = e.pay_to_route_synchronous(payment_hash, route['route'])
        pe = resp['payment_error']
        # print(json.dumps(resp, indent=2))

        if pe:
            hop_error_index = int(pe[-1:]) - 1
            source_pubkey = route['route']['hops'][hop_error_index-1]['pub_key']
            dest_pubkey = route['route']['hops'][hop_error_index]['pub_key']
            s_alias = utils.get_alias(source_pubkey)
            d_alias = utils.get_alias(dest_pubkey)
            print(f'{s_alias} ---> {d_alias}: TCF, removing...\n')
            graph.remove_edge(source_pubkey, dest_pubkey)
        else:
            print(json.dumps(resp, indent=4))
            break

        attempt_number += 1
        if attempt_number <= 100:
            time.sleep(1)
            continue

        break

        # print(json.dumps(resp['payment_error']))

    
    


    
    # my_neighbors = ln_graph.neighbors(
    #     '0323aac79814817b023ce6e4eac13c961df213e773e901f74fa4c9477f22e0f304')
    # for n in my_neighbors:
    #     print(n)

    # forwards = reader.get_all_forwards()

    # forwards_headers = [
    #     'timestamp',
    #     'chan_id_in',
    #     'chan_id_out',
    #     'amt_in',
    #     'amt_out',
    #     'fee',
    #     'fee_msat',
    #     'amt_in_msat',
    #     'amt_out_msat',
    #     'timestamp_ns'
    # ]
    # print(tabulate(forwards, headers=forwards_headers))

    # router.find_route(
    #     '03df3f0a2fd6bea5429a596461ce784c922b2981ada1af89cfefcd9ccfb16c16a7',
    #     1000000
    #     )
    
    




    # 
    # reader.get_node('0323aac79814817b023ce6e4eac13c961df213e773e901f74fa4c9477f22e0f304')
    # reader.get_node_channels('026165850492521f4ac8abd9bd8088123446d126f648ca35e60f88177dc149ceb2')
    # x = router.find_route(
    #     '03df3f0a2fd6bea5429a596461ce784c922b2981ada1af89cfefcd9ccfb16c16a7',
    #     100000
    #     )
    # print(json.dumps(x, indent=4))
    # print(json.dumps(e.get_channels(), indent=2))



    # forward_history = e.get_forwarding_history()
    # forwards = forward_history['forwarding_events']

    # df = r.route_summary(forwards)
    # df = r.forwarding_summary(forwards)

    # res = e.get_htlc_events()
    # for r in res.iter_lines():
    #     json_response = json.loads(r)
    #     print(json_response)
    
