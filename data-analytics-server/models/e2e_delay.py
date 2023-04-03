import numpy as np
import pandas as pd
from utils.graphing import bin_label


def calculate_end_to_end_delay(df: pd.DataFrame, timeframe: int, bins: int) -> pd.DataFrame:
    # calculation depends on bins - NNW ****** need to filter recv records now
    start_point = df['timestamp'].min()
    bin_size = (df['timestamp'].max() - df['timestamp'].min()) / bins
    boundaries = []
    for i in range(bins + 1):
        boundaries.append(start_point + (i * bin_size))
    
    df['bins'] = pd.cut(df['timestamp'], bins=boundaries)
    # calculate network metrics based on timeframe and bins (how far back)
    network_metric = _calculate_metrics(df)

    return network_metric


def _calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:

    # add new column for data only
    df['date'] = df['env_timestamp'].dt.date
    # retrieve send records and received records separately
    df_send_raw=df.loc[df['direction'] == 'send'].copy()
    df_recv_raw=df.loc[df['direction'] == 'recv'].copy()
    # rename timestamp columns
    df_send_raw.rename(columns={"timestamp": "send_ts"}, inplace=True)
    df_recv_raw.rename(columns={"timestamp": "recv_ts"}, inplace=True)
    # join based on packet_id and date
    print(df_recv_raw.columns)
    print(df_send_raw.columns)
    df_recv=pd.merge(df_recv_raw[["packet_id","recv_ts","env_timestamp","date","bins"]],df_send_raw[["packet_id","send_ts","date"]], on=['packet_id','date'], how='left')
    # calculate delay
    df_recv['delay'] = df_recv['recv_ts']-df_recv['send_ts']
    df_recv.to_csv("Nwe_e2e_metric1.csv")
    network_metric = df_recv.groupby('bins').agg({'delay': sum, 'packet_id': 'count', 'env_timestamp': max}).rename(columns={'delay': 'total_delay', 'packet_id': 'total_packets'})  
    network_metric['average_delay'] = network_metric['total_delay'] / network_metric['total_packets']
    network_metric = network_metric.reset_index()
    # Make time format readable
    network_metric['env_timestamp'] = network_metric['env_timestamp'].dt.strftime("%H:%M:%S").astype(str)
    network_metric['bins'] = network_metric.reset_index()['bins'].apply(bin_label)
    network_metric.to_csv("Nwe_e2e_metric2.csv")
    return network_metric
    
