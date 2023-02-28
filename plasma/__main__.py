import plasma.lnd_rest.endpoints as e
import plasma.metrics.routing as r
import plasma.db.db_reader as reader
import plasma.db.db_writer as writer
import plasma.db.db_utils as utils
import plasma.rebalance as router
import plasma.event_listener as listener

import json
import time


if __name__ == "__main__":
    writer.update_dbs(rebuild_network_topology=True)

    # AlphaStreet
    # _from = '0323aac79814817b023ce6e4eac13c961df213e773e901f74fa4c9477f22e0f304'
    
    # Boltz
    _from = '026165850492521f4ac8abd9bd8088123446d126f648ca35e60f88177dc149ceb2'

    # nodl-lnd-s007-001
    # _to = '02691fbf5f161d13640d2c8bc1fcb47a601badfaf5b82e892d75376e3bf540a590'

    # MemecoinKiller
    # _to = '021fdbe0467f99673059db47f2e41a7b9430b200e2bdfdff39a1db0bee8428d069'

    # TK21
    # _to = '039f1f720ddf57f51cc029f6cee7bd56bd57e1fa42146a5106744fa516aefe07c4'

    # FREEDOM
    # _to = '021e9cd0d5417970eb15bfcda0b7628c8f49ef710603577776fa45c5b8ecbca35e'

    # ACINQ
    # _to = '03864ef025fde8fb587d989186ce6a4a186895ee44a926bfc370e2c366597a3f8f'

    # CryptoChill
    _to = '03df3f0a2fd6bea5429a596461ce784c922b2981ada1af89cfefcd9ccfb16c16a7'

    sat_amt = 1000
    max_fee = 3
    max_hops = 10
    favorite_paths = [
        '0323aac79814817b023ce6e4eac13c961df213e773e901f74fa4c9477f22e0f304,026165850492521f4ac8abd9bd8088123446d126f648ca35e60f88177dc149ceb2,02c12363b0f977f2a23e4b9bb8555d2fd30a2ba9649e3bd6d9b00aca9569d43f15,03df3f0a2fd6bea5429a596461ce784c922b2981ada1af89cfefcd9ccfb16c16a7,0323aac79814817b023ce6e4eac13c961df213e773e901f74fa4c9477f22e0f304',
        '0323aac79814817b023ce6e4eac13c961df213e773e901f74fa4c9477f22e0f304,026165850492521f4ac8abd9bd8088123446d126f648ca35e60f88177dc149ceb2,0284a1e2bcd08ad7e204fdd67bdf1e18c711cf225182fa52e60623c189c2393a45,024bfaf0cabe7f874fd33ebf7c6f4e5385971fc504ef3f492432e9e3ec77e1b5cf,02315202505c36fc8d6e70a24a29b8bd046a6fccd81dcbff809226533c572b1d82,03df3f0a2fd6bea5429a596461ce784c922b2981ada1af89cfefcd9ccfb16c16a7,0323aac79814817b023ce6e4eac13c961df213e773e901f74fa4c9477f22e0f304'
    ]

    router.rebalance(
        _from,
        _to,
        sat_amt,
        max_fee,
        max_hops,
        'cheapest',
        favorite_paths
    )


















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
    
