import csv

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