import datetime

import plasma.lnd_rest.endpoints as e
import plasma.db.db_reader as reader
import plasma.db.db_writer as writer
import plasma.db.db_utils as utils

MY_PUBKEY = '0323aac79814817b023ce6e4eac13c961df213e773e901f74fa4c9477f22e0f304'

# TODO: catagorize nodes automatically based on inflow/outflow
NODES = {
    # Crypto-RiS
    '039f6f74de35652c3d804cd873f14cc858e26beb3fda9d14363bae40d94bc72fde': {
        'type': 'source',
        'multiplier': 1
    },
    # 1.ln.aantonop.com
    '0237fefbe8626bf888de0cad8c73630e32746a22a2c4faa91c1d9877a3826e1174': {
        'type': 'standard',
        'multiplier': 1 
    },
    # albatross
    '030112133f62b20f81b76754695a0cbb683552c307a062897123fbf3d6360f394c': {
        'type': 'standard',
        'multiplier': 1
    },
    # BCash_Is_Trash
    '0298f6074a454a1f5345cb2a7c6f9fce206cd0bf675d177cdbf0ca7508dd28852f': {
        'type': 'standard',
        'multiplier': 1
    },
    # Boltz
    '026165850492521f4ac8abd9bd8088123446d126f648ca35e60f88177dc149ceb2': {
        'type': 'standard',
        'multiplier': 1
    },
    # deezy.io
    '024bfaf0cabe7f874fd33ebf7c6f4e5385971fc504ef3f492432e9e3ec77e1b5cf': {
        'type': 'standard',
        'multiplier': 1
    },
    # FrankTheLNTank
    '027f75974fbe3f2f809899aea661c034a61ef03ad264fd3f2eb77ce32f0f8ab6a1': {
        'type': 'standard',
        'multiplier': 1
    },
    # FREEDOM
    '021e9cd0d5417970eb15bfcda0b7628c8f49ef710603577776fa45c5b8ecbca35e': {
        'type': 'standard',
        'multiplier': 1
    },
    # Memecoin Killer
    '021fdbe0467f99673059db47f2e41a7b9430b200e2bdfdff39a1db0bee8428d069': {
        'type': 'standard',
        'multiplier': 1
    },
    # nodl-lnd-s007-001
    '02691fbf5f161d13640d2c8bc1fcb47a601badfaf5b82e892d75376e3bf540a590': {
        'type': 'standard',
        'multiplier': 1
    },
    # sahilc
    '039c02976671ae843608584b5b76a7e3f3bf040371d8b34bf5b3c606bb8f3f00a4': {
        'type': 'standard',
        'multiplier': 1
    },
    # uBITquity
    '02e1462ad8c41ae0c8cc2c6788d2b7e351ef72fb154914ea91d9a28f7641555161': {
        'type': 'standard',
        'multiplier': 1
    },
    # ACINQ
    '03864ef025fde8fb587d989186ce6a4a186895ee44a926bfc370e2c366597a3f8f': {
        'type': 'sink',
        'multiplier': 1
    },
    # CryptoChill
    '03df3f0a2fd6bea5429a596461ce784c922b2981ada1af89cfefcd9ccfb16c16a7': {
        'type': 'sink',
        'multiplier': 1
    },
    # WalletOfSatoshi.com
    '035e4ff418fc8b5554c5d9eea66396c227bd429a3251c8cbc711002ba215bfc226': {
        'type': 'sink',
        'multiplier': 1
    }
}
STANDARD_FEE_STRUCTURE = {
    .10: (0, 100),
    .25: (0, 75),
    .50: (0, 50),
    .75: (0, 20),
    .90: (0, 10),
    1: (0, 1)
}
SOURCE_FEE_STRUCTURE = {
    .10: (0, 20),
    .25: (0, 15),
    .50: (0, 10),
    .75: (0, 5),
    .90: (0, 1),
    1: (0, 0)
}
SINK_FEE_STRUCTURE = {
    .10: (10000, 500),
    .25: (10000, 350),
    .50: (5000, 250),
    .75: (2500, 150),
    .90: (1000, 25),
    1: (1000, 5)
}


def fee_balance():
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')
    logfile = open(f'/home/umbrel/connor/dev/plasma/logs/fee_balance_{current_time}', 'w')
    writer.update_dbs(rebuild_network_topology=True)
    channels = reader.get_local_channels()
    for index, channel in channels.iterrows():
        peer = channel['remote_pubkey']
        if peer in NODES.keys():
            peer_type = NODES[peer]['type']
            peer_fee_multiplier = NODES[peer]['multiplier']
            peer_fee_structure = choose_fee_structure(peer_type)

            chan_id = channel['chan_id']
            chan_cap = channel['capacity']
            chan_balance = channel['local_balance']
            
            chan_info = e.get_channel_info(chan_id)
            chan_point = chan_info['chan_point']
            if chan_info['node1_pub'] == MY_PUBKEY:
                chan_fee_structure = (
                    chan_info['node1_policy']['fee_base_msat'],
                    chan_info['node1_policy']['fee_rate_milli_msat']
                )
            else:
                chan_fee_structure = (
                    chan_info['node2_policy']['fee_base_msat'],
                    chan_info['node2_policy']['fee_rate_milli_msat']
                )

            chan_ratio = chan_balance/chan_cap

            suggested_chan_fee_structure = choose_fee(peer_fee_structure, chan_ratio)
            logfile.write(f'{utils.get_alias(peer)}:\n')
            logfile.write(f'  -Balance: {chan_balance} sat ({round((chan_ratio * 100), 2)}% local)\n')
            logfile.write(f'  -Current fees: {chan_fee_structure[0]} msat, {chan_fee_structure[1]} ppm\n')
            logfile.write(f'  -Suggested fees: {suggested_chan_fee_structure[0]} msat, {suggested_chan_fee_structure[1]} ppm\n')
            
            if (
                int(chan_fee_structure[0]) != int(suggested_chan_fee_structure[0])
            ) or (
                int(chan_fee_structure[1]) != int(suggested_chan_fee_structure[1])
            ):
                update_chan_policy_reponse = e.update_channel_policy(
                    chan_point,
                    suggested_chan_fee_structure[0],
                    suggested_chan_fee_structure[1]
                )
                if len(update_chan_policy_reponse['failed_updates']):
                    logfile.write(f'Error, dumping: {update_chan_policy_reponse["failed_updates"]}\n')
                else:
                    logfile.write('Fees updated\n\n')
            else:
                logfile.write('Fees at suggested rates\n\n')

def choose_fee(fee_structure, chan_ratio):
    for tier_ratio, tier_fees in fee_structure.items():
        if chan_ratio <= tier_ratio:
            return tier_fees


def choose_fee_structure(peer_type):
    if peer_type == 'standard':
        return STANDARD_FEE_STRUCTURE
    elif peer_type == 'source':
        return SOURCE_FEE_STRUCTURE
    elif peer_type == 'sink':
        return SINK_FEE_STRUCTURE



if __name__ == '__main__':
    fee_balance()