from models import MetaLog, PacketLog, TopologyLog
from typing import Union


def get_collection_name(log: Union[MetaLog, PacketLog]) -> str:
    """Resolve the collection name: meta, topology, node based on log type"""
    if isinstance(log, MetaLog):
        return 'metalogs'
    
    if isinstance(log, TopologyLog):
        return 'topology'
    
    return f'node-{log.node}'


def delete_all_collections(client):
  """Delete all topology, metalogs, & packetlog collections in client database"""
  client.get_collection('topology').delete_many({})
  client.get_collection('metalogs').delete_many({})
  for c in client.list_collection_names():
      if c.startswith('node-'):
        client.get_collection(c).delete_many({})