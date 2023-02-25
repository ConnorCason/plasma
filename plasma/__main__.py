import plasma.lnd_rest.endpoints as e
import plasma.metrics.routing as r
import plasma.db.db_reader as reader
import plasma.db.db_writer as writer
import plasma.find_route as router

import json

from tabulate import tabulate

if __name__ == "__main__":
    writer.update_dbs(rebuild_network_topology=False)
    # Build a graph optimized for a 1M sat payment
    router.find_route(
        '03df3f0a2fd6bea5429a596461ce784c922b2981ada1af89cfefcd9ccfb16c16a7',
        1000000
        )
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
    
