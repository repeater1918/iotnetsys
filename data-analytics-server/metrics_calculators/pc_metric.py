import numpy as np
import pandas as pd

def calculate_parent_change_ntwk_metrics(df: pd.DataFrame) -> dict:
    """
    For the given timeframe, return an int showing the total number of parent changes.
    """
    net_pc_metrics = df.loc[df['sub_type'] == 'parent'].drop('_id', axis=1).copy()
    net_pc_metrics['env_timestamp'] = net_pc_metrics['env_timestamp'].dt.strftime("%H:%M:%S").astype(str) 
    net_pc_metrics['average'] = round(net_pc_metrics['sub_type_value'].mean(),2)
    node_pc_metrics = _calculate_parent_change_node_metrics(net_pc_metrics)

    return net_pc_metrics.to_dict('records'), node_pc_metrics


def _calculate_parent_change_node_metrics(df: pd.DataFrame) -> dict:
    """
    For the given timeframe, return a dataframe showing the total number of parent changes per node.
    """
    result = {}
    for node in df['node'].unique():
        result[node] = df.loc[df['node'] == node].to_dict('records')

    return result
