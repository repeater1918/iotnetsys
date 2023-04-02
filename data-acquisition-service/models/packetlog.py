from datetime import datetime
from typing import Dict

from models.base import BaseLog


class PacketLog(BaseLog):
    def __init__(self, timestamp: int, node: int, log: str, env_timestamp: datetime) -> None:
        super().__init__(timestamp, node, log, env_timestamp)

        self.direction: str = log[:4].lower()
        self.packet_id: str = log.split(" ")[1]
        self.type: str = 'packet'

    @staticmethod
    def from_dict(source: Dict):
        return PacketLog(**source)

    @staticmethod
    def from_baselog(base_log: BaseLog):
        return PacketLog(**base_log.to_dict())
