import numpy as np
import pandas as pd
from utils.graphing import bin_label
from typing import Tuple
from datetime import datetime, timedelta
import time

def calculate_received_metrics(df: pd.DataFrame, timeframe: int, bins: int) -> pd.DataFrame:
    df = get_packets_in_timeframe(df, timeframe)
    # calculate bin size
    bin_size = (df['timestamp'].max() - df['timestamp'].min()) / bins
    # preparing bins
    df = prepare_bins(df, bins, bin_size)
    # get first environment timestamp
    env_time_min = df['env_timestamp'].min()
    # limit to recv messages
    df = df.loc[df['direction'] == 'recv'].copy()
    
    metrics_net = calculate_metrics(df, env_time_min, bin_size)
    #metrics_node = calculate_metrics_node(df, env_time_min, bin_size)
    
    return metrics_net

def get_packets_in_timeframe(df: pd.DataFrame, timeframe: int) -> pd.DataFrame:
    # get packets only within timeframe (miliseconds)
    start_timestamp_limit = df['timestamp'].min()
    if timeframe == 0:
        end_timestamp_limit = df['timestamp'].max()
    else:
        end_timestamp_limit = start_timestamp_limit + timeframe
        if (end_timestamp_limit >= df['timestamp'].max()):
            end_timestamp_limit = df['timestamp'].max()
     # filter down to relevant timeframe
    df = df.loc[df['timestamp'] < end_timestamp_limit ].copy()
    return df

def prepare_bins(df: pd.DataFrame, bins: int, bin_size: int) -> pd.DataFrame:
    boundaries = []
    for i in range(bins + 1):
        boundaries.append((df['timestamp'].min() - 1) + (i * bin_size))
    boundaries[-1] = boundaries[-1] + 1
    if df.empty:
        raise Exception('Note enough data for recv')
    df['bins'] = pd.cut(df['timestamp'], bins=boundaries)
    return df
    
def add_env_timestamps(df: pd.DataFrame, env_time_min, bin_size: int) -> pd.DataFrame:
    for i in range(len(df['bins'])): 
        df.loc[i, 'env_timestamp'] = env_time_min + pd.Timedelta(milliseconds=bin_size) * (i+1)
    df['env_timestamp'] = df['env_timestamp'].dt.strftime("%H:%M:%S").astype(str)
    return df

def calculate_metrics(df: pd.DataFrame, env_time_min, bin_size: int) -> pd.DataFrame:
    # group by bins and count packets
    df = df.groupby('bins').agg({'packet_id': 'count'}).rename(columns={'packet_id': 'total_packets'})
    df = df.reset_index()
    # add environment timestamps
    df = add_env_timestamps(df, env_time_min, bin_size)
    # accumulate
    for i in range(1, len(df['total_packets'])): 
        df.loc[i, 'total_packets'] += df.loc[i-1, 'total_packets']
    # apply bin label
    df['bins'] = df.reset_index()['bins'].apply(bin_label)
    return df.to_dict('records')

# def calculate_metrics_node(df: pd.DataFrame, env_time_min, bin_size: int) -> pd.DataFrame:
#     df = df.groupby(['node','bins']).agg({'packet_id': 'count', 'env_timestamp': max}).rename(columns={'packet_id': 'total_packets'})
#     df = df.reset_index()
    
#     df = add_env_timestamps(df, env_time_min, bin_size)
    
#     for node in df['node'].unique():
#         packets = df.loc[df['node'] == node, 'total_packets']
#         for i in range(1, len(packets)): 
#             packets[i] += packets[i-1]
#         df.loc[df['node'] == node, 'total_packets'] = packets
#     breakpoint()
#     df['bins'] = df.reset_index()['bins'].apply(bin_label)
    
#     result = {}
#     for node in df['node'].unique():
#         result[node] = df.loc[df['node'] == node].to_dict('records')
#     #breakpoint()
#     return result