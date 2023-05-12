import numpy as np
import pandas as pd

def calculate_energy_cons_metrics(df: pd.DataFrame) -> pd.DataFrame:
    # Metric calculation using duty cycle value and nodes

    """
    For the given timeframe, return an int showing the total energy consume by all nodes
    
    """
    energy_cons_metrics = df.loc[df['sub_type'] == 'duty'].drop('_id', axis=1).copy()
    energy_cons_metrics = energy_cons_metrics.groupby('sub_type').agg({'sub_type_value3': sum, 'node':'count'})
    energy_cons_metrics["energy_cons"] = energy_cons_metrics["sub_type_value3"]/energy_cons_metrics["node"]
    return energy_cons_metrics
