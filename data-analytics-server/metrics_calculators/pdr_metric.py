import numpy as np
import pandas as pd
from utils.graphing import bin_label
from typing import Tuple


def calculate_pdr_metrics(
    df: pd.DataFrame, timeframe: int, bins: int
) -> Tuple[dict, dict]:
    """Calculates the Packet Delivery Ratio metrics at both the node and network level

    Args:
        df (pd.DataFrame): DataFrame containing all packet metrics
        timeframe (int): The temporal time frame specified by user in front-end (x-axis)
        bins (int): The number of bins used to divide the time frame resulting in discrete ticks on x-axis

    Raises:
        Exception: Generic exception when DataFrame (df) is empty and no data available to calculate metric

    Returns:
        Tuple[dict, dict]: First dict contains metric results for network, second contains results for node
    """

    # calc diff from send and recv
    df["pd_diff"] = df.groupby(["unique_id"])["timestamp"].diff(-1) * -1
    # limit to send messages
    df = df.loc[df["direction"] == "send"].copy()
    #  filter down data frame to relevant time frame
    df = _filter_data_window(df, timeframe)
    # if time to recv is NaN then loss = True
    df["pdr_loss"] = np.where(df["pd_diff"].isna(), True, False)
    # calculation depends on time frame and bins - prepare bins
    start_point = df["timestamp"].min()
    bin_size = (_available_window(df)) / bins
    boundaries = []
    for i in range(bins + 1):
        boundaries.append(start_point + (i * bin_size))
    #  adjust to include min and max value

    if df.empty:
        raise Exception("Note enough data for PDR")

    df["bins"] = pd.cut(df["timestamp"], bins=boundaries, include_lowest=True)
    # calculate network metrics based on timeframe and bins (how far back)
    network_metric = _calculate_network_metrics(df)
    node_metric = _calculate_node_metrics(df)

    return network_metric, node_metric


def _calculate_network_metrics(df: pd.DataFrame) -> dict:
    """ Calculates Network metrics from appropriately filtered packet data

    Args:
        df (pd.DataFrame): Filtered packet data

    Returns:
        dict: Metric results at network level
    """    

    network_metric = (
        df.groupby("bins")
        .agg({"pdr_loss": sum, "packet_id": "count", "env_timestamp": max})
        .rename(columns={"pdr_loss": "failed_packets", "packet_id": "total_packets"})
    )
    network_metric["successful_packets"] = (
        network_metric["total_packets"] - network_metric["failed_packets"]
    )
    network_metric["successful_packets_precentage"] = (
        network_metric["successful_packets"] / network_metric["total_packets"] * 100
    )
    network_metric["failed_packets_precentage"] = (
        network_metric["failed_packets"] / network_metric["total_packets"] * 100
    )
    network_metric = network_metric.reset_index()
    # Make time format readable
    network_metric["env_timestamp"] = (
        network_metric["env_timestamp"].dt.strftime("%H:%M:%S").astype(str)
    )
    network_metric["bins"] = network_metric.reset_index()["bins"].apply(bin_label)

    return network_metric.to_dict("records")


def _calculate_node_metrics(df: pd.DataFrame) -> dict:
    """Calculates Node metrics from appropriately filtered packet data

    Args:
        df (pd.DataFrame): Filtered packet data

    Returns:
        dict: Metric results at node level
    """    

    node_metric = (
        df.groupby(["node", "bins"])
        .agg({"pdr_loss": sum, "packet_id": "count", "env_timestamp": max})
        .rename(columns={"pdr_loss": "failed_packets", "packet_id": "total_packets"})
    )
    node_metric["successful_packets"] = (
        node_metric["total_packets"] - node_metric["failed_packets"]
    )
    node_metric["successful_packets_precentage"] = (
        node_metric["successful_packets"] / node_metric["total_packets"] * 100
    )
    node_metric["failed_packets_precentage"] = (
        node_metric["failed_packets"] / node_metric["total_packets"] * 100
    )
    node_metric = node_metric.reset_index()

    node_metric["env_timestamp"] = (
        node_metric["env_timestamp"].dt.strftime("%H:%M:%S").astype(str)
    )
    node_metric["bins"] = node_metric.reset_index()["bins"].apply(bin_label)
    node_metric = node_metric.dropna()

    # target = {"1": {"pdr_metric": data}}
    result = {}
    for node in node_metric["node"].unique():
        result[node] = node_metric.loc[node_metric["node"] == node].to_dict("records")

    return result


def _available_window(df: pd.DataFrame) -> int:
    """Available window is the delta of the first and last timestamp

    Args:
        df (pd.DataFrame): DataFrame containing all packet metrics

    Returns:
        int: The delta between fist and last time space which represents the window of packet data
    """

    return df["timestamp"].max() - df["timestamp"].min()


def _filter_data_window(df: pd.DataFrame, timeframe: int) -> pd.DataFrame:
    """Data window starts from first packet to:
        (a) Last packet received is the last available packet is before the requested timeframe, OR
        (b) The last packet at or before the requested timeframe if the available window exceeds requested timeframe

    Args:
        df (pd.DataFrame): DataFrame containing all packet metrics
        timeframe (int): The temporal time frame specified by user in front-end (x-axis)

    Returns:
        pd.DataFrame: Packet data filtered to appropriate temporal reference
    """

    max_ts_msg_recv = df.loc[~df["pd_diff"].isna(), "timestamp"].max()
    target_ts_limit = df["timestamp"].min() + timeframe

    # if the latest recv event is before time frame endpoint return cut-off at last recv event
    if max_ts_msg_recv < target_ts_limit:
        return df.loc[df["timestamp"] <= max_ts_msg_recv].copy()

    # return time frame
    return df[df["timestamp"] <= target_ts_limit]
