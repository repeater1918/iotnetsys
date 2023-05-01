import numpy as np
import pandas as pd
from utils.graphing import bin_label


def calculate_dead_loss(df: pd.DataFrame, timeframe: int, timeframe_deadline:int,bins: int, nodeID:int) -> pd.DataFrame:
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
    # check deadline loss or not
    df_joined['deadloss'] = np.where((df_joined['delay'] > timeframe_deadline), 1, 0)
    
    # filter records based on nodeID
    # -1 means Network level, otherwise, node level
    if nodeID!=-1: 
        df_joined=df_joined.loc[df_joined['send_node'] == nodeID]
    
    start_point = df_joined['send_ts'].min()
    bin_size = (df_joined['send_ts'].max() - df_joined['send_ts'].min()) / bins
    boundaries = []
    for i in range(bins + 1):
        boundaries.append(start_point + (i * bin_size))
    
    df_joined['bins'] = pd.cut(df_joined['send_ts'], bins=boundaries, include_lowest=True)
    metric = df_joined.groupby('bins').agg({'deadloss': sum, 'unique_id': 'count', 'env_timestamp': max}).rename(columns={'deadloss': 'total_deadloss','unique_id': 'total_recv_packets'})  
    # calculate deadline loss percent
    metric['deadloss_percent'] = (metric['total_deadloss'] / metric['total_recv_packets'])*100
    metric = metric.reset_index()
    # Make time format readable
    metric['env_timestamp'] = metric['env_timestamp'].dt.strftime("%H:%M:%S").astype(str)
    metric['bins'] = metric.reset_index()['bins'].apply(bin_label)
    return metric

    
    
