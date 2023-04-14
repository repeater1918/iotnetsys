import numpy as np
import pandas as pd
from utils.graphing import bin_label

def calculate_received_metrics(df: pd.DataFrame, timeframe: int, bins: int) -> pd.DataFrame:
    # get packets only within timeframe (miliseconds)
    # get latest timestamp
    timestamp_limit = df['timestamp'].max() - (timeframe * bins)
    # filter down to relevant timeframe
    df = df.loc[df['timestamp'] >= timestamp_limit].copy()
    # limit to recv messages
    df = df.loc[df['direction'] == 'recv'].copy()
    #df = df.reset_index()
    # calculation depends on timeframe and bins - prepare bins
    start_point = df['timestamp'].min() - 1
    bin_size = (df['timestamp'].max() - df['timestamp'].min()) / bins
    boundaries = []
    for i in range(bins + 1):
        boundaries.append(start_point + (i * bin_size))
    
    df['bins'] = pd.cut(df['timestamp'], bins=boundaries)
    
    metrics = df.groupby('bins').agg({'packet_id': 'count', 'env_timestamp': max}).rename(columns={'packet_id': 'total_packets'})
    metrics = metrics.reset_index()
    metrics['env_timestamp'] = metrics['env_timestamp'].dt.strftime("%H:%M:%S").astype(str)
    metrics['bins'] = metrics.reset_index()['bins'].apply(bin_label)
    return metrics


    