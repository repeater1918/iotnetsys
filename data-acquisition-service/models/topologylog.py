from datetime import datetime
from typing import Dict
import time
from models.base import BaseLog


class TopologyLog(BaseLog):
    def __init__(self, node: int, log: str, timestamp: int, sessionid: datetime, env_timestamp: datetime, log_fields: list) -> None:
        super().__init__(timestamp, node, log, sessionid, env_timestamp)        
        self.role = 'sensor'
        self.parent = log_fields[1]
        self.type = 'topology'
        if log_fields[2] != None:
            self.node = log_fields[2]
        self._last_updated = None

    @staticmethod
    def from_dict(source: Dict):
        return TopologyLog(**source)

    @staticmethod
    def from_baselog(base_log: BaseLog):      
        return TopologyLog(**base_log.to_dict())

    def update_topo_attr(self, field, value):
        setattr(self, field, value)
