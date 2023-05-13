import numpy as np
import pandas as pd

def calculate_energy_cons_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates energy consumption metrics: total energy consumed and average energy consumption per node.

    Args:
        df (pd.DataFrame): a datafarme containing containing filtered packet information

    Returns:
        pd.DataFrame: a dataframe containing the average energy consumption per node
    """
    energy_cons_metrics = df.loc[df['sub_type'] == 'duty'].drop('_id', axis=1).copy()
    #energy_cons_ntwk_metrics = energy_cons_metrics.groupby('sub_type').agg({'sub_type_value3': sum, 'node':'count'})
    energy_cons_ntwk_metrics= {'energy_cons': round(energy_cons_metrics["sub_type_value3"].mean(),0)}
    node_energy_metrics = calculate_energy_cons_node_metrics(energy_cons_metrics)
    return energy_cons_ntwk_metrics, node_energy_metrics


def calculate_energy_cons_node_metrics(df: pd.DataFrame) -> dict:
    """
    Calculates the total parent changes for each node.

    Args:
        df (pd.DataFrame): a dataframe containing filtered packet information

    Returns:
        dict: a dict mapping the the total number of parent changes to a node ID
    """
    result = {}
    node_df = df.groupby('node')['sub_type_value3'].mean().reset_index().rename(columns={'sub_type_value3': 'energy_cons'}) 
    for node in node_df['node']:
        result[node] = node_df.loc[node_df['node'] == node].to_dict('records')

    return result
