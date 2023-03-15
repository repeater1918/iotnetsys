
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

import os
import subprocess
import time
from pathlib import Path

import psutil
from dotenv import load_dotenv
from pymongo import MongoClient

dotenv_path = Path(".envs/mongodb.env")
load_dotenv(dotenv_path=dotenv_path)

MONGO_ATLAS_URI = f"mongodb+srv://{os.getenv('MONGO_USR')}:{os.getenv('MONGO_PWD')}@{os.getenv('MONGO_CLSTR')}"

# Connect to mongo instance and define starting db = iotnetsys - and table = netsys-live
client = MongoClient(MONGO_ATLAS_URI)
db = client["iotnetsys"]
collection = db["netsys-live"]

# Instruct python to run Omid's script and pipe the results to this program
target_script = (
    "emitter.bat"  # NOTE: change this to emitter.sh if you are working in linux/mac
)

proc = subprocess.Popen(
    [target_script],
    shell=True,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

PID = proc.pid


def get_proc_status(pid):
    """Get the status of the process which has the specified process id."""

    proc_status = None

    try:
        proc_status = psutil.Process(pid).status()
    except psutil.Error as no_proc_exc:
        proc_status = no_proc_exc
    finally:
        return proc_status


while True:
    time.sleep(
        5
    )  # HACK - delays input response by 1 second for readability
    # read terminal input
    response = proc.stdout.readline().decode()

    if response:
        # Send data to MongoDB
        data = {"data": response}
        _id = collection.insert_one(data).inserted_id
        print(
            f"saved to MongoDB: {_id} - response= {response} - {get_proc_status(PID)}"
        )

    elif response == "":
        # Sad path or closure
        print(get_proc_status(PID))
        break
    else:
        # Unknown path
        print("unkown event")

# Terminate process
proc.terminate()
