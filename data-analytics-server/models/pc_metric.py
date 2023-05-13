def calculate_parent_change_metrics(df: pd.DataFrame, timeframe: int, bins: int) -> pd.DataFrame:
    """
    For the given timeframe, return a dataframe with the total number of parent changes.
    """
    timestamp_limit = df['timestamp'].max() - (timeframe * bins)
    # filter down to relevant timeframe
    df = df.loc[df['timestamp'] >= timestamp_limit].copy()

    parent_changes = 0
    for index, row in df.iterrows():
        log: str = row['log']
        if 'parentChange' in log:
            log_parts = log.split()
            parent_changes += int(log_parts[1])

    return parent_changes

