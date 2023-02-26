import csv
import pandas as pd

import plasma.db.db_reader as reader

def write_lod_to_csv(lod, csv_name):
    keys = lod[0].keys()
    with open(csv_name, 'w') as outfile:
        dw = csv.DictWriter(outfile, keys)
        dw.writeheader()
        dw.writerows(lod)

def get_alias(pubkey):
    alias_df = reader.get_network_nodes()[
        ['pub_key', 'alias']
    ]
    pubkey_df = alias_df[alias_df['pub_key'] == pubkey]
    return pubkey_df.iloc[0]['alias']

def get_chan_id_of_peers(pubkey1, pubkey2):
    channels = reader.get_network_channels()
    
    n12_df = channels[
        (channels['node1_pub'] == pubkey1) &
        (channels['node2_pub'] == pubkey2)
    ]
    n21_df = channels[
        (channels['node1_pub'] == pubkey2) &
        (channels['node2_pub'] == pubkey1)
    ]
    ret_df = pd.concat([
        n12_df,
        n21_df
    ])

    chan_id = int(ret_df.iloc[0]['channel_id'])
    return chan_id