from typing import Union

from models.base import BaseLog
from models.metalog import MetaLog
from models.packetlog import PacketLog
from datetime import datetime


def parse_incoming(data: str, start_time: datetime) -> Union[MetaLog, PacketLog]:
    """ Converts to a basic log object and idenitifies what type of log -> MetaLog or PacketLog"""
    base_log = BaseLog.from_string(data, start_time)
    log = _identify_log(base_log)
    return log


def _identify_log(base_log: BaseLog) -> Union[MetaLog, PacketLog]:
    """ Reads field to determine if log was packet or Meta - transform object accordingly"""
    if base_log.log[:4] not in ("Send", "Recv"):
        return MetaLog.from_baselog(base_log)
    else:
        return PacketLog.from_baselog(base_log)
