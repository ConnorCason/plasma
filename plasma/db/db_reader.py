import pandas as pd
from tabulate import tabulate

def get_local_channels():
    return pd.read_csv('plasma/db/local_channels.csv')

def get_local_forwards():
    return pd.read_csv('plasma/db/local_forwards.csv')

def get_network_channels():
    return pd.read_csv('plasma/db/network_channels.csv')

def get_network_nodes():
    return pd.read_csv('plasma/db/network_nodes.csv')


def get_node(pubkey):
    nodes_df = pd.read_csv('plasma/db/network_nodes.csv')
    node_row = nodes_df.loc[nodes_df['pub_key'] == pubkey]
    final = node_row.loc[:, node_row.columns != 'features']
    pd.set_option('max_colwidth', 20)
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 500)
    print(final)
    return final

def get_node_channels(pubkey, _print=False):
    channels_df = pd.read_csv('plasma/db/network_channels.csv')
    node_channels = channels_df.loc[
        (channels_df['node1_pub'] == pubkey) |
        (channels_df['node2_pub'] == pubkey)
        ]

    with_node1_aliases = pd.merge(
        node_channels,
        get_network_nodes()[['pub_key', 'alias']],
        left_on='node1_pub',
        right_on='pub_key',
        how='left'
    ).rename(
        columns={'alias': 'node1_alias'}
    )

    with_aliases = pd.merge(
        with_node1_aliases,
        get_network_nodes()[['pub_key', 'alias']],
        left_on='node2_pub',
        right_on='pub_key',
        how='left'
    ).rename(
        columns={'alias': 'node2_alias'}
    ).reset_index()

    if _print:
        ordered_aliases = pd.concat([
                with_aliases[with_aliases['node1_pub'] == pubkey],
                with_aliases[with_aliases['node2_pub'] == pubkey]
        ])[[
                'node1_alias',
                'capacity',
                'node2_alias'
            ]]

        print(tabulate(ordered_aliases))

    return with_aliases
