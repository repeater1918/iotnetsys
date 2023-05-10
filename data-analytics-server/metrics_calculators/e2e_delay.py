import numpy as np
import pandas as pd
from utils.graphing import bin_label

def calculate_end_to_end_delay(df: pd.DataFrame, timeframe: int, bins: int, nodeID:int) -> pd.DataFrame:
   # calc diff from send and recv
    df["delay"] = df.groupby(["unique_id"])["timestamp"].diff(-1) * -1
    # limit to send messages
    df = df.loc[(df["direction"] == "send")&(~df["delay"].isna())].copy()
    # add new column for date only
    df['date'] = df['env_timestamp'].dt.date
    # calculate delay
    
    # filter records based on nodeID
    # -1 means Network level, otherwise, node level
    if nodeID!=-1: 
        df=df.loc[df['node'] == nodeID]
    # calculation depends on bins
    start_point = df["timestamp"].min()
    bin_size = (df["timestamp"].max() - df["timestamp"].min()) / bins
    boundaries = []
    for i in range(bins + 1):
        boundaries.append(start_point + (i * bin_size))
    df['bins'] = pd.cut(df['timestamp'], bins=boundaries, include_lowest=True)
    
    metric = df.groupby('bins').agg({'delay': sum, 'unique_id': 'count', 'env_timestamp': max}).rename(columns={'delay': 'total_delay', 'unique_id': 'total_recv_packets'})  
    metric['average_delay'] = metric['total_delay'] / metric['total_recv_packets']
    metric = metric.reset_index()
    # Make time format readable
    metric['env_timestamp'] = metric['env_timestamp'].dt.strftime("%H:%M:%S").astype(str)
    metric['bins'] = metric.reset_index()['bins'].apply(bin_label)
    
    return metric


    
