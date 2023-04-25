import pandas as pd
import numpy as np


def topology_df_gen(df: pd.DataFrame):
    df = df[['node','role','parent']]
    df = df.fillna(value={'role':'sensor'})
    # #filter down empty list and fill with itself
    # mask = df['parent'].map(len) == 0
    # df['parent'] = np.where(mask, df['node'].values, df['parent'].values)
    # df['parent'] = df['parent'].apply(lambda x: [x] if isinstance(x, int) else x)
    # #apply direct parent
    # df['direct_parent'] = [l[0] for l in df['parent']].copy()
    return df