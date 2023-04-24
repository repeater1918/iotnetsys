from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Union
import re 

class BaseLog(object):

    def __init__(self, timestamp: int, node: int, log: str, env_timestamp: datetime) -> None:
        self.timestamp = int(timestamp)
        self.node = node if isinstance(node, int) else int(node[3:])
        self.log = log
        self.env_timestamp = env_timestamp + timedelta(milliseconds=self.timestamp)
        self.log_fields = self.extract_log_fields()

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
    
    
    def to_database(self) -> Dict:
        return {k:v for k,v in self.__dict__.items() if not k.startswith(('_', 'log_fields'))}
    

    def extract_log_fields(self) -> str:
        """ Parse all the log into appropriate fields 
        Format: [subtype(i.e directions),'','',logvalue,logtype]
        """
        try:
            log_fields =  list(re.search(r'(INFO|Recv|Send|icmp|drop|parent|duty)([a-zA-Z]*\W{0,1}\s*)?(.*Node ID: )?(\d+)?',self.log).groups())
        except:
            #Non-supported log detected
            return []
        if log_fields[0].lower() == 'info':
            if log_fields[3] != None: 
                log_fields.append('topology')
            else:
                #Unsupported INFO message
                return []
        elif log_fields[0].lower() in ('recv','send'):
            log_fields.append('packet')
        else:
            log_fields.append('meta')

        return log_fields
    

    def __repr__(self) -> str:
        return str(self.to_dict())
    


