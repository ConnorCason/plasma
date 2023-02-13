import config


def get_routing_metrics(forwards):
    for f in forwards:
        print(f)

        # print(f"Made {f['fee']} settling {f['']}")




# def get_routing_metrics(forwards):
    # daily_seconds = 86400
    # time_deltas = {
    #     'day': time() - (1*daily_seconds),
    #     'week': time() - (7*daily_seconds),
    #     'month': time() - (30*daily_seconds),
    #     'year': time() - (365*daily_seconds),
    #     'all time': time() - (3000*daily_seconds)
    # }

    # for delta in time_deltas:
    #     curr_col = {
    #         'settled': 0,
    #         'forwards': 0,
    #         'fee': 0
    #     }
    #     for f in forwards:
    #         settled = f['amt_in']
    #         fee = f['fee']
    #         if f['timestamp'] >= time_deltas[delta]: