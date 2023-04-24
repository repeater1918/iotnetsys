"""
DAS

Runs a target script and reads the results from the terminal.
The reponse from the terminal is sent a cloud instance of MongoDB (Mongo Atlas)
Program ends when underlying script ends

TODO:

1. Define schemas so DAS can convert input from IOT to a MongoDB format
2. Processing logic to separte important elemnts of IOT packets into MongoDB document format
3. Decide what tables / databases we will need and what information is fed into them
4. How will we store IOT data - as sessions (each unique time a script is started so Omid can refer back to a prior reading)

"""
from pathlib import Path

from dotenv import load_dotenv

dotenv_path = Path(Path(__file__).parent.resolve(), "../.envs/mongodb.env")
load_dotenv(dotenv_path=dotenv_path)

import subprocess, os
import time
from datetime import datetime

import psutil
from database.mongodb import Database
from models import parse_incoming, PacketLog, TopologyLog
from utils import get_collection_name, delete_all_collections

dotenv_path = Path(Path(__file__).parent.resolve(), "../.envs/mongodb.env")
load_dotenv(dotenv_path=dotenv_path)

# Connect to local mongo instance and define starting db = iotnetsys
client = Database(database_name="iotnetsys")

# Instruct python to run Omid's script and pipe the results to this program
target_script = ("emitter.sh")
#Windows os will use below script
if os.name == 'nt':
    target_script = ("emitter.bat")

proc = subprocess.Popen(
    [target_script],
    shell=True,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

PID = proc.pid
START_TIMESTAMP = datetime.utcnow()
global node_dict
node_dict = {}

def get_proc_status(pid):
    """Get the status of the process which has the specified process id."""

    proc_status = None

    try:
        proc_status = psutil.Process(pid).status()
    except psutil.Error as no_proc_exc:
        proc_status = no_proc_exc
    finally:
        return proc_status


def update_topology_dict(nodeid: int, log_dict):
    """ Update the topology dictionary in runtime 
        If the node is not in memory, cre
        TODO: handle dynamic parent, when parent is unknown in advance, and when parent change during network ops
    """
    global node_dict
    collection = client.get_collection('topology')
    res = 'No update'
    if nodeid not in node_dict.keys():        
        topo = TopologyLog(nodeid, "Generated from Packet event")
        node_dict[nodeid] = topo
        db_entry = topo.to_database()
        res = collection.insert_one(db_entry).inserted_id

    else:
        topo = node_dict[nodeid]
        # Assume the role is updated only one time, no change during run
        # If Role is not updated, update based on packet direction
        if (node_dict[nodeid].role == 'sensor'):
            
            #Simulate a static topology, no ways to know direct parent as now
            #May need to seek Omid help for mechanism to inform the direct parent
            if topo.parent[0] == nodeid:
                if nodeid in (2,3):
                    topo.parent[0] = 1
                elif nodeid in (4,5):
                    topo.parent[0] = 2
                else:
                    topo.parent[0] = 3
                topo._last_updated = time.time()
          
            if (log_dict['direction'] == 'recv'):
                #Only server has receive message                
                node_role = 'server'
                topo.role = node_role
                topo._last_updated = time.time()


            sender_id = int(log_dict['packet_id'][:3])
            if (log_dict['direction'] == 'send') and (sender_id != nodeid):
                #To implement list of parent nodes, when the sensor sends a packet differnt with its id
                #it indicates that this sensor will be a parent for the packet sender, would append to list as we have timing order
                if sender_id not in topo.parent:
                    topo.parent.append(sender_id)
                    topo._last_updated = time.time()

            if topo._last_updated < time.time() + 1:
                db_entry = topo.to_database()
                res = collection.update_one({"node": nodeid}, 
                                            {"$set": db_entry}).acknowledged
            
    return res

delete_all_collections(client) #to refresh db after each DAS run 

while not proc.poll():
    time.sleep(0)  # FIXME - delays input response by 1 second for readability

    # read terminal input
    response = proc.stdout.readline().decode()

    if response:
        # Send data to MongoDB
        data = {"data": response}["data"]
        # Delegate object identification to models / inheritance
        log = parse_incoming(data, START_TIMESTAMP)
        if log == None:
            continue
       
        #Add node to topology runtime memory
        if isinstance(log, TopologyLog):
            node_dict[log.node] = log 

        #Database operations        
        log_dict = log.to_database()
        #Update the topology runtime memory
        if isinstance(log, PacketLog):
            res = update_topology_dict(nodeid=int(log_dict['node']),log_dict=log_dict)          
            #print(f"Updated result is {res}")
        

        # if packet log collection = 'packetlogs' else 'metalogs' -> send to mongoDB
        collection = client.get_collection(get_collection_name(log)) 
        _id = collection.insert_one(log_dict).inserted_id

        print(_id, log_dict, get_collection_name(log))

    elif response == "":
        # Sad path or closure
        print(get_proc_status(PID))
        break
    else:
        # Unknown path
        print("unkown event")

# Terminate process
proc.terminate()
