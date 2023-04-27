import numpy as np
import pandas as pd

def calculate_parent_change_ntwk_metrics(df: pd.DataFrame) -> dict:
    """
    For the given timeframe, return an int showing the total number of parent changes.
    """
    # filter down to relevant meta packets (parent changes)
    df = df.loc[df['sub_type'] == 'parent'].copy()
    # calc network metric dictionary with network result
    network_parent_changes = len(df)
    #  format as required
    ntwk_result_dict = [{'network_parent_changes': network_parent_changes}]

    return ntwk_result_dict


def calculate_parent_change_node_metrics(df: pd.DataFrame) -> dict:
    """
    For the given timeframe, return a dataframe showing the total number of parent changes per node.
    """
    # filter down to relevant meta packets (parent changes)
    df = df.loc[df['sub_type'] == 'parent'].copy()
    # initialise counts for nodes 1 to 7
    df = df.groupby('node').agg({'_id': 'count'}).reset_index().rename(columns={'_id': 'total_parent_changes'})
    #  format as required
    node_result_dict = {}
    for node in df['node'].unique():
        node_result_dict[node] = df.loc[df['node'] == node].to_dict('records')

    # target = {"1": {"pdr_metric": data}}
    return node_result_dict