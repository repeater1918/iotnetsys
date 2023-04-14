from models import MetaLog, PacketLog
from typing import Union


def get_collection_name(log: Union[MetaLog, PacketLog]) -> str:
    
    if isinstance(log, MetaLog):
        return 'metalogs'
    
    return f'node-{log.node}'