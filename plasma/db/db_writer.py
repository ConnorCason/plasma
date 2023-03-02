import time

import plasma.lnd_rest.endpoints as e
import plasma.db.db_utils as utils


def update_dbs(rebuild_network_topology=False):
    write_forwards()
    write_channels()
    print()
    if rebuild_network_topology:
        write_network_topology()

def write_forwards():
    all_forwards = e.get_forwarding_history()
    utils.write_lod_to_csv(all_forwards, 'plasma/db/local_forwards.csv')
    print('Forwarding history updated')

def write_channels():
    all_channels = e.get_channels()
    utils.write_lod_to_csv(all_channels, 'plasma/db/local_channels.csv')
    print('Active channels updated')


def write_network_topology(nodes_only=False, channels_only=False):
    s = time.time()
    print('Updating network topology...')
    graph = e.get_graph()
    if not channels_only:
        utils.write_lod_to_csv(graph['nodes'], 'plasma/db/network_nodes.csv')
    if not nodes_only:
        utils.write_lod_to_csv(graph['edges'], 'plasma/db/network_channels.csv')
    print(f'Network topology updated in {round((time.time() - s), 2)} seconds\n')





