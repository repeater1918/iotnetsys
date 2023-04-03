import numpy as np
import pandas as pd

def calculate_queue_loss(df: pd.DataFrame) -> pd.DataFrame:
    queueloss_metrics = df.loc[df['sub_type'] == 'drop'].drop('_id', axis=1).copy()
    queueloss_metrics['env_timestamp'] = queueloss_metrics['env_timestamp'].astype(str)
    #breakpoint()
    return queueloss_metrics

"""
def calculate_queue_loss(df: pd.DataFrame) -> float:
    queueloss_metrics = df.loc[df['sub_type'] == 'drop'].drop('_id', axis=1).copy()
    queueloss_metrics['env_timestamp'] = pd.to_datetime(queueloss_metrics['env_timestamp'])
    latest_timestamp = queueloss_metrics['env_timestamp'].max()
    latest_value = queueloss_metrics.loc[queueloss_metrics['env_timestamp'] == latest_timestamp, 'value'].sum()
    return latest_value
"""
