import pandas as pd
import plotly
import plotly.express as px

# 1201362 ID:2 parentChange 6
# 1201426 ID:4 parentChange 2
# 'log': 'SendData 005219'
def calculate_parent_change_metrics(df: pd.DataFrame, timeframe: int, bins: int) -> pd.DataFrame:
    