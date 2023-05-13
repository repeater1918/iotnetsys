import pandas as pd
import numpy as np


def topology_df_gen(df: pd.DataFrame):
    """
    Generates a IoT network topology dataframe.

    Args:
        df (pd.DataFrame): a dataframe containing filtered packet information

    Returns:
        pd.DataFrame: a topology dataframe containing node, role, parent and hop count information
    """
    df = df[['node','role','parent']]
    df = df.fillna(value={'role':'sensor'})

    #find server node  
    server_node = df.loc[df['role'] == 'server', 'node'].values.tolist()
    # loop through all the nodes in the dataframe
    if len(server_node) > 0:
        for nodeid in df['node'].values:   
            if nodeid in server_node:
                df.loc[df['node'] == nodeid, 'hop_count'] = 0
                continue
            # find the path and hop count to the root node
            path, hop_count = _find_path_to_root(df, nodeid, server_node)       
            # assign the hop count to a new column in the dataframe
            df.loc[df['node'] == nodeid, 'hop_count'] = hop_count

        df = df.fillna(value={'hop_count': 0})
        df = df.astype({'hop_count':'int'})

    return df

def _find_path_to_root(df, nodeid, server_node):
    """
    Finds the path and hop count from a node to the root node.

    Args:
        df: a dataframe containing filtered packet information
        nodeid: node ID
        server_node: server node ID

    Returns:
        Tuple[List[Any], int]: the path from the node to the root node, the hop count from the node to the root node
    """
    # find the server node by looking for the node with no parent
    #server_node = df.loc[df['role'] == 'server', 'node'].values[0]
    # initialize an empty list to store the path
    path = []
    
    # loop until the server node is reached
    hop_count = 0
    while nodeid not in server_node:
        # add the current node and its role to the path
        if nodeid in df['node'].values:
            role = df.loc[df['node'] == nodeid, 'role'].values[0]       
        else:
            break
        # find the parent of the current node
        parent = df.loc[df['node'] == nodeid, 'parent'].values[0]   
        path.append(parent)     
        # set the parent as the new current node
        nodeid = parent
        
        #calculate hop count
        hop_count += 1
   
    
    # reverse the path so that it starts from the server node
    path.reverse()    

    return path, hop_count