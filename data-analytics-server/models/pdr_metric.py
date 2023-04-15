import numpy as np
import pandas as pd
from utils.graphing import bin_label
from typing import Tuple


def calculate_pdr_metrics(df: pd.DataFrame, timeframe: int, bins: int) -> Tuple[dict, dict]:
    # set pdr limit
    df['pdr_lim'] = 5000
    # calc diff from send and recv
    df['pd_diff'] = df.groupby(['packet_id'])['timestamp'].diff(-1) * -1
    # if time to recv > pdr_lim then loss = True
    df['pdr_loss'] = np.where(df['pd_diff'] > df['pdr_lim'], True, False)
    # calcuale time between all messages and latest message
    df['ts_diff'] = (df['timestamp'] - df['timestamp'].max()) * -1
    # limit to send messages
    df = df.loc[df['direction'] == 'send'].copy()
    # if packet send and time between sending the packet and the latest pack (i.e. now) is > pdr_limit assume packet was lost
    df['packet_loss'] = np.where((df['ts_diff'] > df['pdr_lim'])&(df['pd_diff'].isna()), True, False)
    # pdr loss is when send/recv differ is > pdr limit or packet is lost (not recv within timeframe)
    df['pdr_loss'] = df[['packet_loss', 'pdr_loss']].max(axis=1)
    # ingnore recent packets within pdr loss timeframe
    df = df.loc[(df['ts_diff'] > df['pdr_lim'])]
    # get packets only within timeframe (miliseconds)
    # get latest timestamp
    timestamp_limit = df['timestamp'].max() - (timeframe * bins)
    # filter down to relevant timeframe
    df = df.loc[df['timestamp'] >= timestamp_limit].copy()

    # calculation depends on timeframe and bins - prepare bins
    start_point = df['timestamp'].min() - 1
    bin_size = (df['timestamp'].max() - df['timestamp'].min()) / bins
    boundaries = []
    for i in range(bins + 1):
        boundaries.append(start_point + (i * bin_size))
    
    df['bins'] = pd.cut(df['timestamp'], bins=boundaries)

    # calculate network metrics based on timeframe and bins (how far back)
    network_metric = _calculate_network_metrics(df)
    node_metric = _calculate_node_metrics(df)

    return network_metric, node_metric


def _calculate_network_metrics(df: pd.DataFrame) -> pd.DataFrame:
    network_metric = df.groupby('bins').agg({'pdr_loss': sum, 'packet_id': 'count', 'env_timestamp': max}).rename(columns={'pdr_loss': 'failed_packets', 'packet_id': 'total_packets'})  
    network_metric['successful_packets'] = network_metric['total_packets'] - network_metric['failed_packets']
    network_metric['successful_packets_precentage'] = network_metric['successful_packets'] / network_metric['total_packets'] * 100
    network_metric['failed_packets_precentage'] = network_metric['failed_packets'] / network_metric['total_packets'] * 100
    network_metric = network_metric.reset_index()
    # Make time format readable
    network_metric['env_timestamp'] = network_metric['env_timestamp'].dt.strftime("%H:%M:%S").astype(str)
    network_metric['bins'] = network_metric.reset_index()['bins'].apply(bin_label)
    
    return network_metric.to_dict('records')

def _calculate_node_metrics(df: pd.DataFrame) -> pd.DataFrame:
    node_metric = df.groupby(['node','bins']).agg({'pdr_loss': sum, 'packet_id': 'count', 'env_timestamp': max}).rename(columns={'pdr_loss': 'failed_packets', 'packet_id': 'total_packets'})
    node_metric['successful_packets'] = node_metric['total_packets'] - node_metric['failed_packets']
    node_metric['successful_packets_precentage'] = node_metric['successful_packets'] / node_metric['total_packets'] * 100
    node_metric['failed_packets_precentage'] = node_metric['failed_packets'] / node_metric['total_packets'] * 100
    node_metric = node_metric.reset_index()

    node_metric['env_timestamp'] = node_metric['env_timestamp'].dt.strftime("%H:%M:%S").astype(str)
    node_metric['bins'] = node_metric.reset_index()['bins'].apply(bin_label)

    # target = {"1": {"pdr_metric": data}}
    result = {}
    for node in node_metric['node'].unique():
        result[node] = {"pdr_metric": node_metric.loc[node_metric['node'] == node].to_dict('records')}

    return result


