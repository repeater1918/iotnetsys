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
import sys
from dotenv import load_dotenv

dotenv_path = Path(Path(__file__).parent.resolve(), "../.envs/mongodb.env")
load_dotenv(dotenv_path=dotenv_path)

import subprocess, os
import time
from datetime import datetime
import copy  
import psutil
from database.mongodb import Database
from models import parse_incoming, PacketLog, TopologyLog, MetaLog
from utils import get_collection_name, delete_all_collections

# Connect to local mongo instance and define starting db
client = Database(database_name="iotnetsys")

# Resolve IOT runnable path
if os.getenv('DEMO_STATE') == True:
    target_script = ("emitter.bat") if os.name == 'nt' else ("emitter.sh")
elif len(sys.argv) < 2:
    print("Please provide the path to the shell or batch runnable for IOT procedure")
    sys.exit(1)
elif len(sys.argv) > 2:
    print(f"Data service expected one argument 'path_to_runnable' but {len(sys.argv) - 1} were provided")
    sys.exit(1)
else:
    target_script = (sys.argv[1])

# Execute target runnable
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



def update_topology_dict(log, log_type):
    """ Update the topology dictionary in runtime                 
    """
    global node_dict
    collection = client.get_collection('topology')
    nodeid = int(log.node)
    res = 'No update'
    db_insert = True
    if log_type == 'packet':
        if nodeid not in node_dict.keys():
            #Node doesnt exist in db 
            topo = TopologyLog(nodeid, "Generated from Packet event", log.timestamp,log.sessionid, log.env_timestamp,log.log_fields)
            topo.role = 'server' if log.direction == 'recv' else 'sensor'
            topo.parent = nodeid                       
            node_dict[nodeid] = topo  
            db_insert = True
            #print("Insert to database object created automatically")            
        else:
            db_insert = False
            if (log.direction == 'recv'): 
                if (node_dict[nodeid].role == 'sensor'):
                    #Promote the sensor to be server                    
                    node_dict[nodeid].role = 'server'                    
                    node_dict[nodeid]._last_updated = time.time()                       
                    #print("promote ev")
                else:
                    #Parent of the sender (sensor) is not init, assumed it's directly connected to server
                    nodeid = int(log.packet_id[:3]) #pointer to sender
                    if nodeid in node_dict.keys():      
                        #sensor must be known, if not, it's a malicious packet                 
                        if node_dict[nodeid].parent == nodeid: #parent value and nodeid are same (not init yet)
                            node_dict[nodeid].parent = int(log.node)
                            node_dict[nodeid]._last_updated = time.time()
                            #print("updated parent for sensor from pkt ev")  

    if log_type == 'topology':
        #Handle current node
        if nodeid not in node_dict.keys():
            #Node doesnt exist, insert it
            node_dict[nodeid] = log
            db_insert = True
            #print(f"Insert a record from topology event to database")           
        else:
            #Node is known, hence just updated based on the log             
            node_dict[nodeid] = log
            node_dict[nodeid]._last_updated = time.time()   
            db_insert = False
            #print(f"Update database with a topology info {log.log}")       

        #Handle the parent from the message, since the topology is 2-way, the child inform the parent (or parent inform the child)               
        if (log.parent not in node_dict.keys()):
                parentid = log.parent
                parent_topo = copy.deepcopy(log)
                parent_topo.node = parentid
                #Init the parent also, if it doesnt existw
                node_dict[parentid] = parent_topo
                res = collection.insert_one(parent_topo.to_database()).inserted_id 
                   
    topo = node_dict[nodeid]
    if topo._last_updated != None:              
        if time.time() - topo._last_updated < 2:   
            db_entry = topo.to_database()
            #print(f"Topology Database is updated with record {db_entry}")
            res = collection.find_one_and_update({"node": nodeid}, {"$set": db_entry}, 
                                                sort=[('_id', -1)], return_document=True)
    elif db_insert == True:
        res = collection.insert_one(topo.to_database()).inserted_id

    return res


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
            #print("skipped", response)
            continue       
        
        #Handle dynamic topology data
        update_topology_dict(log=log, log_type=log.type)
        #Database operations        
        if isinstance(log, PacketLog) or isinstance(log, MetaLog):
        # if packet log collection = 'packetlogs' else 'metalogs' -> send to mongoDB
            collection = client.get_collection(get_collection_name(log)) 
            log_dict = log.to_database()
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
