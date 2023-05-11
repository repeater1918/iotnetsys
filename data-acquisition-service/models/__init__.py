from typing import Union

from models.base import BaseLog
from models.metalog import MetaLog
from models.packetlog import PacketLog
from models.topologylog import TopologyLog
from datetime import datetime


def parse_incoming(data: str, start_time: datetime) -> Union[MetaLog, PacketLog]:
    """ Converts to a basic log object and idenitifies what type of log -> MetaLog or PacketLog"""
    try:
        base_log = BaseLog.from_string(data, start_time)
        
    except:
        #Spurious log message detected
        return None 
    log = _identify_log(base_log)

    return log


def _identify_log(base_log: BaseLog) -> Union[MetaLog, PacketLog, TopologyLog, BaseLog]:
    """ Reads field to determine if log was packet or Meta - transform object accordingly"""

    if len(base_log.log_fields) == 5:
        if base_log.log_fields[4] == 'topology':
            return TopologyLog.from_baselog(base_log)
        elif base_log.log_fields[4] == 'packet':
            return PacketLog.from_baselog(base_log)    
        else:
            return MetaLog.from_baselog(base_log)
        

    