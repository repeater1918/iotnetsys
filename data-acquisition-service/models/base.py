from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Union
import re 
import copy

class BaseLog(object):

    def __init__(self, timestamp: int, node: int, log: str, start_timestamp: datetime, env_timestamp: datetime) -> None:
        self.timestamp = int(timestamp)
        self.sessionid = start_timestamp
        self.node = node if isinstance(node, int) else int(node[3:])
        self.log = log
        self.env_timestamp = start_timestamp + timedelta(milliseconds=self.timestamp)
        self.log_fields = self.extract_log_fields()

    @staticmethod
    @abstractmethod
    def from_dict(input: Dict):
        pass

    @staticmethod
    def from_string(input: str, start_timestamp: datetime):
        components = input.strip().split('\t') + [start_timestamp] + [start_timestamp]
        return BaseLog(*components)

    def to_dict(self) -> Dict:
        return {k:v for k,v in self.__dict__.items() if k[0] != '_'}
    
    
    def to_database(self) -> Dict:
        return {k:v for k,v in self.__dict__.items() if not k.startswith(('_', 'log_fields'))}
    

    def extract_log_fields(self) -> str:
        """ Parse all the log into appropriate fields 
        Format: [subtype(i.e directions),'','',logvalue,logtype]
        """                   
                    
        pattern_list = ['(add_uplink|add_downlink).*(from)+.*(\s+\d+)',                    
                        '(SendData|RecvData|duty|icmp|parent|drop)([a-zA-Z]*\W{0,1}\s*)?(\d+)(\s+\d+)?(\s+\d+)?']
        log_fields = []
        returned_field = [] #[subtype(i.e directions),'','',logvalue,logtype]
        for pattern in pattern_list:
            try:
                log_fields = list(re.search(pattern, self.log).groups())
                break 
            except:
                continue
        
        if len(log_fields) == 5:  
    
            returned_field = [log_fields[0],log_fields[2], None, None, 'meta']
            if log_fields[3] != None and log_fields[4] != None:
                returned_field[2] = int(log_fields[3])
                returned_field[3] = int(log_fields[4])

            if returned_field[0].lower() in ('senddata','recvdata'):
                returned_field[0] = log_fields[0][:4]
                returned_field[4] = 'packet'                      

                
        elif len(log_fields) == 3:
            returned_field = [log_fields[0],int(log_fields[2]), self.node, log_fields[1], 'topology']
            if ("add_uplink" in log_fields[0] and "from" in log_fields[1]):
                returned_field[1] = self.node
                returned_field[2] = int(log_fields[2]) #swap position
         
        return returned_field

        
    

    def __repr__(self) -> str:
        return str(self.to_dict())
    


