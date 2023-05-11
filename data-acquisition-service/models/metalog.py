import re
from datetime import datetime
from typing import Dict

from models.base import BaseLog
from datetime import timedelta

class MetaLog(BaseLog):
    def __init__(self, timestamp: int, sessionid: datetime, node: int, log: str, env_timestamp: datetime, log_fields: list) -> None:
        super().__init__(timestamp, node, log, sessionid, env_timestamp)
        self.type = log_fields[4]
        sub_type, sub_type_value = (log_fields[0],log_fields[1])
        sub_type_value2, sub_type_value3 = (log_fields[2], log_fields[3])
        self.sub_type: str = sub_type
        self.sub_type_value: int = int(sub_type_value)
        if sub_type_value2 != None and sub_type_value3 != None:
            self.sub_type_value2: int = int(sub_type_value2)
            self.sub_type_value3: int = int(sub_type_value3)


    @staticmethod
    def from_dict(source: Dict):
        return MetaLog(**source)

    @staticmethod
    def from_baselog(base_log: BaseLog):
        return MetaLog(**base_log.to_dict())
    
    def _resolve_meta_sub_type(self):
        regex = re.search(r'(icmp|drop|parent|duty)([a-zA-Z]*\W{0,1}\s*)(\d+)', self.log)
        return (regex.group(1),  regex.group(3))
    