import pandas as pd
from typing import Union, List, Dict


class TopologyStream(object):
    # stores all historical packets
    df_packet_hist: pd.DataFrame = pd.DataFrame(
        columns=["node", "parent", "role"]
    )
    # buffer for new packets - added to df_packet_hist periodically
    stream: List[Dict] = []

    is_update_ready: bool = False

    def __init__(self, packet_update_limit: int) -> None:
        self.packet_update_limit = packet_update_limit

    def append_stream(self, documents: List[Dict]):
        """Adds  new packets to a raw stream and checks if enough are in the stream to flag update"""
        self.stream = self.stream + documents
        # if the stream has accumulated enough packets, flag update is ready
        if len(self.stream) > self.packet_update_limit:
            self.is_update_ready = True

    def flush_stream(self):
        """Move the new packet to history dataframe"""
        self._move_packets_to_df_packet_hist()
        self._prepare_data_types()                   

        self.stream.clear()
        self.is_update_ready = False
        return self.df_packet_hist

    def _refresh_stream(self):
        """Empties the raw stream and resets counter for next update notification"""
        self.stream.clear()
        self.is_update_ready = False

    def delete_df(self):
        """Delete both stream & dataframe to prepare for new session"""
        self.stream.clear()
        self.df_packet_hist = pd.DataFrame(columns=self.df_packet_hist.columns)
        self.is_update_ready = False

    def _move_packets_to_df_packet_hist(self) -> None:
        """Move the raw packet stream (list) to dataframe history"""
        self.df_packet_hist = pd.concat(
            [pd.DataFrame(self.stream),self.df_packet_hist]
        )
        self.df_packet_hist = self.df_packet_hist.sort_values(
            "node", ascending=True
        ).reset_index(drop=True)
    

    def _prepare_data_types(self) -> None:
        """Converts to correct datatypes"""
        self.df_packet_hist["node"] = self.df_packet_hist["node"].astype(int)
