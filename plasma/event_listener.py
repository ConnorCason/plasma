import json

import plasma.lnd_rest.endpoints as e


if __name__ == '__main__':
    print('Listening for HTLC events...')
    htcl_event_stream = e.get_htlc_events()
    for event in htcl_event_stream.iter_lines():
        event_str = json.dumps(json.load(event), indent=4)
        print(event_str)
        with open('htlc_events.txt', 'a') as eventsfile:
            eventsfile.write(f'{event_str}\n\n')