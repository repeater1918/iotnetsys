from datetime import datetime
from typing import Dict

from models.base import BaseLog


class PacketLog(BaseLog):
    def __init__(self, timestamp: int, sessionid: datetime, node: int, log: str, env_timestamp: datetime, log_fields: list) -> None:
        super().__init__(timestamp, node, log, env_timestamp)
        self.sessionid = sessionid
        self.type = log_fields[4]
        self.direction: str = log_fields[0].lower()
        self.packet_id: str = log_fields[1]


    @staticmethod
    def from_dict(source: Dict):
        return PacketLog(**source)

    @staticmethod
    def from_baselog(base_log: BaseLog):
        return PacketLog(**base_log.to_dict())
