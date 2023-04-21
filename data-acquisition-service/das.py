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

import subprocess
import time
from datetime import datetime

import psutil
from database.mongodb import Database
from models import parse_incoming
from utils import get_collection_name

dotenv_path = Path(Path(__file__).parent.resolve(), "../.envs/mongodb.env")
load_dotenv(dotenv_path=dotenv_path)

# Connect to local mongo instance and define starting db = iotnetsys
client = Database(database_name="iotnetsys")

# Instruct python to run Omid's script and pipe the results to this program
target_script = (
    "emitter.sh"  # NOTE: change this to emitter.sh if you are working in linux/mac
)

proc = subprocess.Popen(
    [target_script],
    shell=True,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

PID = proc.pid
START_TIMESTAMP = datetime.utcnow()


def get_proc_status(pid):
    """Get the status of the process which has the specified process id."""

    proc_status = None

    try:
        proc_status = psutil.Process(pid).status()
    except psutil.Error as no_proc_exc:
        proc_status = no_proc_exc
    finally:
        return proc_status


while not proc.poll():
    time.sleep(1)  # FIXME - delays input response by 1 second for readability

    # read terminal input
    response = proc.stdout.readline().decode()

    if response:
        # Send data to MongoDB
        data = {"data": response}["data"]
        # Delegate object identification to models / inheritance
        log = parse_incoming(data, START_TIMESTAMP)
        # if packet log collection = 'packetlogs' else 'metalogs' -> send to mongoDB
        collection = client.get_collection(get_collection_name(log)) 
        _id = collection.insert_one(log.to_dict()).inserted_id

        print(_id, log, get_collection_name(log))

    elif response == "":
        # Sad path or closure
        print(get_proc_status(PID))
        break
    else:
        # Unknown path
        print("unkown event")

# Terminate process
proc.terminate()
