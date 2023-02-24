import plasma.lnd_rest.endpoints as e
import plasma.metrics.routing as r
import plasma.db.db_writer as d
import plasma.find_route as router

import json


if __name__ == "__main__":

    d.update_dbs()
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
    
