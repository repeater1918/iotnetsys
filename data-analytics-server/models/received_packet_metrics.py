import numpy as np
import pandas as pd
from utils.graphing import bin_label

def calculate_received_metrics(df: pd.DataFrame, timeframe: int, bins: int) -> pd.DataFrame:

    end_time = int(df["timestamp"].max()) # Get the maximum timestamp in the dataframe
    start_time = end_time - timeframe # Calculate the end time based on the timeframe
    
    # Filter dataframe for packets received in the given timeframe
    timeframe_df = df[(df["timestamp"] >= start_time) & (df["timestamp"] < end_time) & (df["direction"] == "recv")].drop('_id', axis=1)
    
    start_point = timeframe_df['timestamp'].min() - 1
    bin_size = (timeframe_df['timestamp'].max() - timeframe_df['timestamp'].min()) / bins
    
    boundaries = []
    for i in range(bins + 1):
        boundaries.append(start_point + (i * bin_size))
    
    timeframe_df['bins'] = pd.cut(timeframe_df['timestamp'], bins=boundaries)
    
    metrics = timeframe_df.groupby('bins').agg({ 'packet_id': 'count', 'env_timestamp': max}).rename(columns={'packet_id': 'total_packets'})
    metrics = metrics.reset_index()
    metrics['env_timestamp'] = metrics['env_timestamp'].dt.strftime("%H:%M:%S").astype(str)
    metrics['bins'] = metrics.reset_index()['bins'].apply(bin_label)
    #breakpoint()
    return metrics


    