import numpy as np
import pandas as pd
from utils.graphing import bin_label
from typing import Tuple
from datetime import datetime, timedelta
import time

def calculate_received_metrics(df: pd.DataFrame, timeframe: int, bins: int) -> Tuple[dict, dict]:
    """
    Calculates the number of received packets within a specified timeframe.

    Args:
        df (pd.DataFrame): a dataframe containing filtered packet information
        timeframe (int): duration of the timeframe in milliseconds
        bins (int): number of bins in which to divide the timeframe

    Returns:
        Tuple[dict, dict]: a tuple containing received metrics calculations at the network and node levels
    """
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
    """
    Filter packet dataframe to include packets within a specified timeframe.

    Args:
        df (pd.DataFrame): a dataframe containing filtered packet information
        timeframe (int): duration of the timeframe in milliseconds

    Returns:
        pd.DataFrame: a filtered dataframe containing packets within the specified timeframe
    """
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
    
def add_env_timestamps(df: pd.DataFrame, env_time_min, bin_size: int) -> pd.DataFrame:
    """
    Adds environment timestamps to the dataframe.

    Args:
        df (pd.DataFrame): a dataframe containing filtered packet information
        env_time_min (_type_): the minimum environment timestamp
        bin_size (int): the size of each bin

    Returns:
        pd.DataFrame: a dataframe with the added 'env_timestamp' column
    """
    for i in range(len(df['bins'])): 
        df.loc[i, 'env_timestamp'] = env_time_min + pd.Timedelta(milliseconds=bin_size) * (i+1)
    df['env_timestamp'] = df['env_timestamp'].dt.strftime("%H:%M:%S").astype(str)
    return df

def calculate_metrics(df: pd.DataFrame, env_time_min, bin_size: int) -> pd.DataFrame:
    """
    _summary_

    Args:
        df (pd.DataFrame): a dataframe containing filtered packet information
        env_time_min (_type_): the minimum environment timestamp
        bin_size (int): the size of each bin

    Returns:
        pd.DataFrame: _description_
    """
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
