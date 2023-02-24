import json
import plasma.lnd_rest.endpoints as e

def find_route(dest_pubkey, sat_amt):
    routes = e.get_routes(dest_pubkey, sat_amt)
    print(f'Found {len(routes)} viable routes')
    print(json.dumps(routes, indent=4))