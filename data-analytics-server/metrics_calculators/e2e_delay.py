import numpy as np
import pandas as pd
from utils.graphing import bin_label
from typing import Tuple

def calculate_end_to_end_delay(df: pd.DataFrame, timeframe: int, bins: int) -> Tuple[dict, dict]:
    """ Calculate Network level OR Node levle end-to-end delay based on passed nodeID parameter

    Args:
        df (pd.DataFrame): Filtered packet data
        timeframe (int) : user's preferred timeframe (the packet data will be filterred from the beginning to that timeframe)
        nodeID (int) : if nodeID is -1, the function will calculate network level metric. Otherwise, the function will calculate node level metrics
    Returns:
        dict: Metric results at network level or node level according to the nodeID parameter
    """  
   # filter down to relevant timeframe
    start_timestamp_limit = df['timestamp'].min()
    end_timestamp_limit = start_timestamp_limit + timeframe
    df = df.loc[df['timestamp'] <= end_timestamp_limit ].copy()
    # add new column for date only
    df['date'] = df['env_timestamp'].dt.date
    # retrieve send records and received records separately
    df_send_raw=df.loc[df['direction'] == 'send'].copy()
    df_recv_raw=df.loc[df['direction'] == 'recv'].copy()
    # rename timestamp columns
    df_send_raw.rename(columns={"timestamp": "send_ts","node": "send_node"}, inplace=True)
    df_recv_raw.rename(columns={"timestamp": "recv_ts","node": "recv_node"}, inplace=True)
    # join based on packet_id and date
    df_joined=pd.merge(df_send_raw[["send_node","unique_id","send_ts","env_timestamp","date"]],df_recv_raw[["recv_node","unique_id","recv_ts","date"]], on=['unique_id','date'], how='right')
    # calculate delay
    df_joined['delay'] = df_joined['recv_ts']-df_joined['send_ts']
    
    # filter records based on nodeID
    # -1 means Network level, otherwise, node level
    sensor_nodes = [x for x in df_joined['send_node'].unique() if not pd.isnull(x)] 
    node_metric_dict = {}
    if len(sensor_nodes) >0: 
        for node in sensor_nodes:
            df_joined_node=df_joined.loc[df_joined['send_node'] == node].copy()
            node_metric_dict[node] = calculate_average_e2e(df_joined_node, bins)

    # calculation depends on bins
    metric = calculate_average_e2e(df_joined, bins)
    return metric, node_metric_dict

def calculate_average_e2e(df_joined: pd.DataFrame, bins: int) -> dict:
    """        
    Calculate e2e with given number of bins (i.e data points)
    :param df_joined: Processed panda dataframe to joined send/recv events
    :param bins: number of bins

    :return metric dictionary
    
    """
    # calculation depends on bins
    start_point = df_joined['send_ts'].min()
    bin_size = (df_joined['send_ts'].max() - df_joined['send_ts'].min()) / bins
    boundaries = []
    for i in range(bins + 1):
        boundaries.append(start_point + (i * bin_size))
    df_joined['bins'] = pd.cut(df_joined['send_ts'], bins=boundaries, include_lowest=True)
    
    metric = df_joined.groupby('bins').agg({'delay': sum, 'unique_id': 'count', 'env_timestamp': max}).rename(columns={'delay': 'total_delay', 'unique_id': 'total_recv_packets'})  
    metric['average_delay'] = metric['total_delay'] / metric['total_recv_packets']
   
    metric = metric.reset_index()
    # Make time format readable
    metric['env_timestamp'] = metric['env_timestamp'].dt.strftime("%H:%M:%S").astype(str)
    metric['bins'] = metric.reset_index()['bins'].apply(bin_label)
    metric = metric.dropna()
    return metric.to_dict('records')
    
