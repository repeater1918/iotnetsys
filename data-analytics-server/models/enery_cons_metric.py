import numpy as np
import pandas as pd

def calculate_energy_cons_metrics(df: pd.DataFrame) -> pd.DataFrame:
    energy_cons_metrics = df.loc[df['sub_type'] == 'duty'].drop('_id', axis=1).copy()
    energy_cons_metrics = energy_cons_metrics.groupby('sub_type').agg({'sub_type_value': sum, 'node':'count'})
    energy_cons_metrics["energy_cons"] = energy_cons_metrics["sub_type_value"]/energy_cons_metrics["node"]
    energy_cons_metrics.to_csv("test.csv")
    return energy_cons_metrics
