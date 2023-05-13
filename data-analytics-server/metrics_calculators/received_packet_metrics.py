import numpy as np
import pandas as pd
from utils.graphing import bin_label
from typing import Tuple
from datetime import datetime, timedelta
import time

def calculate_received_metrics(df: pd.DataFrame, timeframe: int, bins: int) -> dict:
    """Calculates the Packet Delivery Ratio metrics at network level

    Args:
        df (pd.DataFrame): DataFrame containing all packet metrics
        timeframe (int): The temporal time frame specified by user in front-end (x-axis)
        bins (int): The number of bins used to divide the time frame resulting in discrete ticks on x-axis

    Returns:
        dict: The dict contains metric results for network
    """
    # filtering down data frame to relevant timeframe
    df = get_packets_in_timeframe(df, timeframe)
    # calculating bin size
    bin_size = (df['timestamp'].max() - df['timestamp'].min()) / bins
    # preparing bins
    df = prepare_bins(df, bins, bin_size)
    # get first environment timestamp of relevant dataframe
    min_env_ts = df['env_timestamp'].min()
    # limit to received packets
    df = df.loc[df['direction'] == 'recv'].copy()
    
    # calculate number of recv packets in network
    metrics_network = calculate_metrics(df, min_env_ts, bin_size)
    
    return metrics_network

# filtering down data frame to relevant timeframe
def get_packets_in_timeframe(df: pd.DataFrame, timeframe: int) -> pd.DataFrame:
    end_timestamp_limit = df['timestamp'].min() + timeframe
    if (end_timestamp_limit > df['timestamp'].max()):            
        end_timestamp_limit = df['timestamp'].max()
    # filter down to relevant timeframe
    df = df.loc[df['timestamp'] < end_timestamp_limit].copy()
    return df

#preparing bins 
def prepare_bins(df: pd.DataFrame, bins: int, bin_size: int) -> pd.DataFrame:
    """
    Assigns bins to the dataframe based on packet timestamps.

    Args:
        df (pd.DataFrame): a dataframe containing filtered packet information
        bins (int): number of bins in which to divide the timestamp
        bin_size (int): the size of each bin

    Raises:
        Exception: raised if the dataframe is empty

    Returns:
        pd.DataFrame: a dataframe with the added 'bins' column
    """
    boundaries = []
    for i in range(bins + 1):
        boundaries.append((df['timestamp'].min() - 1) + (i * bin_size))
    boundaries[-1] = boundaries[-1] + 1
    if df.empty:
        raise Exception('Note enough data for recv')
    df['bins'] = pd.cut(df['timestamp'], bins=boundaries)
    return df

#calculating number of recv packets
def calculate_metrics(df: pd.DataFrame, env_time_min, bin_size: int) -> dict:
    # group by bins and count packets
    df = df.groupby('bins').agg({'packet_id': 'count'}).rename(columns={'packet_id': 'total_packets'})
    df = df.reset_index()
    # add environment timestamps to the bins
    df = add_env_timestamps(df, env_time_min, bin_size)
    # accumulate
    for i in range(1, len(df['total_packets'])): 
        df.loc[i, 'total_packets'] += df.loc[i-1, 'total_packets']
    # apply bin label
    df['bins'] = df.reset_index()['bins'].apply(bin_label)
    return df.to_dict('records')

#adding environment timestamps for each bin
def add_env_timestamps(df: pd.DataFrame, env_time_min, bin_size: int) -> pd.DataFrame:
    for i in range(len(df['bins'])): 
        df.loc[i, 'env_timestamp'] = env_time_min + pd.Timedelta(milliseconds=bin_size) * (i+1)
    df['env_timestamp'] = df['env_timestamp'].dt.strftime("%H:%M:%S").astype(str)
    return df
