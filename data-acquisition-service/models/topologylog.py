from datetime import datetime
from typing import Dict
import time
from models.base import BaseLog


class TopologyLog(BaseLog):
    def __init__(self, timestamp: int, sessionid: datetime, node: int, log: str, env_timestamp: datetime, log_fields: list) -> None:
        super().__init__(timestamp, node, log,  env_timestamp)
        self.sessionid = sessionid
        self.type = log_fields[4]
        self.role = 'sensor'
        self.parent = node
        self._last_updated = None

    @staticmethod
    def from_dict(source: Dict):
        return TopologyLog(**source)

    @staticmethod
    def from_baselog(base_log: BaseLog):      
        return TopologyLog(**base_log.to_dict())

    def update_topo_attr(self, field, value):
        setattr(self, field, value)
