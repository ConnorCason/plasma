import pandas as pd

from time import time

DAILY_EPOCH = 86400

_str_to_int = ['timestamp', 'amt_in', 'amt_out', 'fee']

def convert_df_cols(df):
    for col in _str_to_int:
        df[col] = pd.to_numeric(df[col])

def get_forwards_for_window(forwards, window=3650):
    df = pd.DataFrame(forwards)
    convert_df_cols(df)

    window_condition = df['timestamp'] > \
        (time() - (window * DAILY_EPOCH))
    return df[window_condition]
    
def get_routing_metrics_for_window(forwards, window):
    metric_df = get_forwards_for_window(forwards, window)
    count = metric_df.shape[0]
    rev = metric_df['fee'].sum()
    return (count, rev)

def forwarding_summary(forwards):
    df = pd.DataFrame(columns=['days', 'forwards', 'fees'])
    for d in [1,7,30,365]:
        (c, r) = get_routing_metrics_for_window(forwards, d)
        df.loc[len(df.index)] = [d, c, r]
    print(df)
    return df
    
def route_summary(forwards):
    df = get_forwards_for_window(forwards)
    paths_df = df.groupby(['chan_id_in', 'chan_id_out']) \
        .size() \
        .to_frame('travels') \
        .sort_values(['travels'], ascending=False)
    
    print(paths_df)

def interupt():
    import sys
    sys.exit()