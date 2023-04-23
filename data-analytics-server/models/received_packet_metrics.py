import numpy as np
import pandas as pd
from utils.graphing import bin_label
from typing import Tuple
from datetime import datetime, timedelta
import time

def calculate_received_metrics(df: pd.DataFrame, timeframe: int, bins: int) -> Tuple[dict, dict]:
    # get packets only within timeframe (miliseconds)
    start_timestamp_limit = df['timestamp'].min()
    end_timestamp_limit = start_timestamp_limit + timeframe
     # filter down to relevant timeframe
    df = df.loc[df['timestamp'] < end_timestamp_limit ].copy()
    # calculation depends on timeframe and bins - prepare bins
    start_point = df['timestamp'].min() - 1
    bin_size = (df['timestamp'].max() - df['timestamp'].min()) / bins
    # limit to recv messages
    df = df.loc[df['direction'] == 'recv'].copy()
    boundaries = []
    for i in range(bins + 1):
        boundaries.append(start_point + (i * bin_size))
    df['bins'] = pd.cut(df['timestamp'], bins=boundaries)
    
    env_time_min = df['env_timestamp'].min()
    metrics_net = calculate_metrics(df, env_time_min, bin_size)
    metrics_node = calculate_metrics_node(df)
    return metrics_net, metrics_node

def calculate_metrics(df: pd.DataFrame, env_time_min, bin_size: int) -> pd.DataFrame:
    metrics_network = df.groupby('bins').agg({'packet_id': 'count'}).rename(columns={'packet_id': 'total_packets'})
    metrics_network = metrics_network.reset_index()
    
    #accumulation and env_timestamp
    metrics_network.loc[0, 'env_timestamp'] = env_time_min + pd.Timedelta(milliseconds=bin_size)
    for i in range(1, len(metrics_network['total_packets'])): 
        metrics_network.loc[i, 'total_packets'] += metrics_network.loc[i-1, 'total_packets']
        metrics_network.loc[i, 'env_timestamp'] = env_time_min + pd.Timedelta(milliseconds=bin_size) * (i+1)
    #breakpoint()
    metrics_network['env_timestamp'] = metrics_network['env_timestamp'].dt.strftime("%H:%M:%S").astype(str)
    metrics_network['bins'] = metrics_network.reset_index()['bins'].apply(bin_label)
    
    return metrics_network.to_dict('records')

def calculate_metrics_node(df: pd.DataFrame) -> pd.DataFrame:
    node_metric = df.groupby(['node','bins']).agg({'packet_id': 'count', 'env_timestamp': max}).rename(columns={'packet_id': 'total_packets'})
    node_metric = node_metric.reset_index()

    for node in node_metric['node'].unique():
        packets = node_metric.loc[node_metric['node'] == node, 'total_packets']
        for i in range(1, len(packets)): 
            packets[i] += packets[i-1]
        node_metric.loc[node_metric['node'] == node, 'total_packets'] = packets
    
    node_metric['env_timestamp'] = node_metric['env_timestamp'].dt.strftime("%H:%M:%S").astype(str)
    node_metric['bins'] = node_metric.reset_index()['bins'].apply(bin_label)
    
    result = {}
    for node in node_metric['node'].unique():
        result[node] = node_metric.loc[node_metric['node'] == node].to_dict('records')
    #breakpoint()
    return result


    