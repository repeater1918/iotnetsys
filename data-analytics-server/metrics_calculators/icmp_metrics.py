import numpy as np
import pandas as pd
from typing import Tuple

def calculate_icmp_metrics(df: pd.DataFrame) -> Tuple[dict, dict]: 
    """
    Calculates the Internet Control Message Protocol (ICMP) metric over the IoT network.

    Args:
        df (pd.DataFrame): a dataframe containing filtered packet information

    Returns:
        Tuple[dict, dict]: _description_
    """
    net_icmp_metrics = df.loc[df['sub_type'] == 'icmp'].drop('_id', axis=1).copy()
    net_icmp_metrics['env_timestamp'] = net_icmp_metrics['env_timestamp'].dt.strftime("%H:%M:%S").astype(str) 
    node_icmp_metrics = _calculate_node_metrics(net_icmp_metrics)
    return net_icmp_metrics.to_dict('records'), node_icmp_metrics

def _calculate_node_metrics(net_metrics: pd.DataFrame) -> dict:
    """
    Calculates the Internet Control Message Protocol (ICMP) metric for each node.


    Args:
        net_metrics (pd.DataFrame): a dataframe containing filtered packet information 

    Returns:
        dict: a dictionary representing the node-level ICMP metrics
    """
    result = {}
    for node in net_metrics['node'].unique():
        result[node] = net_metrics.loc[net_metrics['node'] == node].to_dict('records')

    return result