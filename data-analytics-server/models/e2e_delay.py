import numpy as np
import pandas as pd
from utils.graphing import bin_label


def calculate_end_to_end_delay(df: pd.DataFrame, timeframe: int, bins: int, nodeID:int) -> pd.DataFrame:
    # add new column for date only
    df.to_csv("e2e_original.csv")
    df['date'] = df['env_timestamp'].dt.date
    # retrieve send records and received records separately
    df_send_raw=df.loc[df['direction'] == 'send'].copy()
    df_recv_raw=df.loc[df['direction'] == 'recv'].copy()
    df_send_raw.to_csv("e2e_sendonly.csv")
    df_recv_raw.to_csv("e2e_receiveonly.csv")
    # rename timestamp columns
    df_send_raw.rename(columns={"timestamp": "send_ts","node": "send_node"}, inplace=True)
    df_recv_raw.rename(columns={"timestamp": "recv_ts","node": "recv_node"}, inplace=True)
    # join based on packet_id and date
    df_joined=pd.merge(df_send_raw[["send_node","packet_id","send_ts","env_timestamp","date"]],df_recv_raw[["recv_node","packet_id","recv_ts","date"]], on=['packet_id','date'], how='left')
    # calculate delay
    df_joined['delay'] = df_joined['recv_ts']-df_joined['send_ts']
    
    # filter records based on nodeID
    # -1 means Network level, otherwise, node level
    if nodeID!=-1: 
        df_joined=df_joined.loc[df_joined['send_node'] == nodeID]
    
    df_joined.to_csv(f'e2e_raw_node{nodeID}.csv')
    # calculation depends on bins
    start_point = df_joined['send_ts'].min()
    bin_size = (df_joined['send_ts'].max() - df_joined['send_ts'].min()) / bins
    boundaries = []
    for i in range(bins + 1):
        boundaries.append(start_point + (i * bin_size))
    df_joined['bins'] = pd.cut(df_joined['send_ts'], bins=boundaries, include_lowest=True)
    df_joined.to_csv(f'e2e_rawWithBin_node{nodeID}.csv')

    metric = df_joined.groupby('bins').agg({'delay': sum, 'packet_id': 'count', 'env_timestamp': max}).rename(columns={'delay': 'total_delay', 'packet_id': 'total_send_packets'})  
    metric['average_delay'] = metric['total_delay'] / metric['total_send_packets']
    metric = metric.reset_index()
    # Make time format readable
    metric['env_timestamp'] = metric['env_timestamp'].dt.strftime("%H:%M:%S").astype(str)
    metric['bins'] = metric.reset_index()['bins'].apply(bin_label)
    metric.to_csv(f'e2e_metric_node{nodeID}.csv')
    return metric

    
