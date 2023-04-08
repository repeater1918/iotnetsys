import numpy as np
import pandas as pd

def calculate_parent_change_ntwk_metrics(df: pd.DataFrame, timeframe: int, bins: int) -> int:
    """
    For the given timeframe, return an int showing the total number of parent changes.
    """
    # get packets only within timeframe (miliseconds)
    # get latest timestamp
    timestamp_limit = df['timestamp'].max() - (timeframe * bins)
    # filter down to relevant timeframe
    df = df[df['timestamp'] >= timestamp_limit]

    network_parent_changes = len(df[df['log'].str.contains('parentChange')])

    return network_parent_changes


def calculate_parent_change_node_metrics(df: pd.DataFrame, timeframe: int, bins: int) -> pd.DataFrame:
    """
    For the given timeframe, return a dataframe showing the total number of parent changes per node.
    """
    # get packets only within timeframe (miliseconds)
    # get latest timestamp
    timestamp_limit = df['timestamp'].max() - (timeframe * bins)
    # filter down to relevant timeframe
    df = df[df['timestamp'] >= timestamp_limit]

    # initialise counts for nodes 1 to 7
    counts = {node_id: 0 for node_id in range(1, 8)}

    # iterate over each row in the filtered dataframe and update the counts
    for index, row in df.iterrows():
        node = row["node"]
        if node in counts and "parentChange" in row["log"]:
            counts[node] += 1

    # create a new dataframe using the updated counts
    node_parent_changes = pd.DataFrame(list(counts.items()), columns=["node", "parent_changes"])

    return node_parent_changes