import numpy as np
import pandas as pd

def calculate_queue_loss(df: pd.DataFrame) -> pd.DataFrame:
    queueloss_metrics = df.loc[df['sub_type'] == 'drop'].drop('_id', axis=1).copy()
    #queueloss_metrics = queueloss_metrics.reset_index()
    queueloss_metrics['env_timestamp'] = queueloss_metrics['env_timestamp'].astype(str)
    #breakpoint()
    return queueloss_metrics
