from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Union


class BaseLog(object):

    def __init__(self, timestamp: int, node: int, log: str, env_timestamp: datetime) -> None:
        self.timestamp = int(timestamp)
        self.node = node if isinstance(node, int) else int(node[3:])
        self.log = log
        self.env_timestamp = env_timestamp + timedelta(milliseconds=self.timestamp)
   
    @staticmethod
    @abstractmethod
    def from_dict(input: Dict):
        pass

    @staticmethod
    def from_string(input: str, start_timestamp: datetime):
        components = input.strip().split('\t') + [start_timestamp]
        return BaseLog(*components)

    def to_dict(self) -> Dict:
        return {k:v for k,v in self.__dict__.items() if k[0] != '_'}
    
    def __repr__(self) -> str:
        return str(self.to_dict())
    


