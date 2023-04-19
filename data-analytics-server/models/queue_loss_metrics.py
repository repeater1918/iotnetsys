import numpy as np
import pandas as pd
from typing import Tuple

def calculate_queue_loss(df: pd.DataFrame) -> Tuple[dict, dict]:
    queueloss_network = df.loc[df['sub_type'] == 'drop'].drop('_id', axis=1).copy()
    queueloss_network['env_timestamp'] = queueloss_network['env_timestamp'].astype(str)
    queueloss_network_dict = queueloss_network.to_dict('records')

    #for nodes
    queueloss_node_dict = {}
    for node in queueloss_network['node'].unique():
        queueloss_node_dict[node] = queueloss_network.loc[queueloss_network['node'] == node].to_dict('records')
    
    return queueloss_network_dict, queueloss_node_dict
