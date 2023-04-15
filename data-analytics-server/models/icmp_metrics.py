import numpy as np
import pandas as pd

def calculate_icmp_metrics(df: pd.DataFrame) -> pd.DataFrame:
    icmp_metrics = df.loc[df['sub_type'] == 'icmp'].drop('_id', axis=1).copy()
    icmp_metrics['env_timestamp'] = icmp_metrics['env_timestamp'].astype(str)
    return icmp_metrics