import numpy as np
import pandas as pd
from typing import Tuple

def calculate_queue_loss(df: pd.DataFrame) -> Tuple[dict, dict]:
    queueloss_network = df.loc[df['sub_type'] == 'drop'].drop('_id', axis=1).copy()
    queueloss_network['env_timestamp'] = queueloss_network['env_timestamp'].dt.strftime("%H:%M:%S").astype(str) 
    queueloss_network_dict = queueloss_network.to_dict('records')
    queueloss_node_dict = calc_queue_loss_nodes(queueloss_network)
    
    return queueloss_network_dict, queueloss_node_dict
    
    #for nodes
def calc_queue_loss_nodes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the queue loss metric at the node level.

    Args:
        df (pd.DataFrame): a dataframe containing filtered packet information

    Returns:
        pd.DataFrame: a dataframe containing the queue loss metrics for individual nodes
    """
    queueloss_node_dict = {}
    for node in df['node'].unique():
        queueloss_node_dict[node] = df.loc[df['node'] == node].to_dict('records')
    
    return queueloss_node_dict
 

