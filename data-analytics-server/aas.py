"""
AAS:
Watches mongoDB for update - decides when to send data to front-end - responds to front end requests

TODO:

1. Define schemas so AAS knows what type of document was inserted (send/rec/scmp etc.)
2. Based on front end requirments decide when and how to send updates to front-end
3. Add processing logic to calculation metrics 

"""

import os
import threading
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from pymongo import MongoClient

dotenv_path = Path(Path(__file__).parent.resolve(), "../.envs/mongodb.env")
load_dotenv(dotenv_path=dotenv_path)

FRONT_END_URL = "http://127.0.0.1:8050/data-update"
MONGO_ATLAS_URI = f"mongodb+srv://{os.getenv('MONGO_USR')}:{os.getenv('MONGO_PWD')}@{os.getenv('MONGO_CLSTR')}"

# Connect to local mongo instance and define starting db = iotnetsys - and table = netsys-live
client = MongoClient(MONGO_ATLAS_URI)
db = client["iotnetsys"]
collection = db["netsys-live"]

app = FastAPI()

global response_history
response_history = 0
global update_event
update_event = datetime.now()


# We will use these as API end points when the user (via Dashboard)
@app.get("/")
async def root():
    return {"message": str(response_history)}


# This is a callback function that is triggered when an update occurs in mongoDB netsys-live table
# In this instance we are sending the update to the front end server by
# a post request if the last update was more than 12 seconds ago
def on_data_change_callback(response):
    global response_history, update_event
    response_history = response_history + 1
    update_time = datetime.now()
    seconds_since_last_update = (update_time - update_event).seconds

    print(seconds_since_last_update)

    if seconds_since_last_update > 12:
        print("sending update to front-end")

        data = {"UPDATE_COUNT": response_history}

        try:
            req = requests.post(url=FRONT_END_URL, json=data) # FIXME this may need to go into a thread/coroutine as it is blocking
            print(req)
        except requests.exceptions.Timeout as e:
            print(f'Timeout sending data to dash = {e}')
            # Maybe set up for a retry, or continue in a retry loop
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            print(f'Could not reach front-end - is server running? - {e}')

        update_event = datetime.now()



# a data watch function that blocks the main thread
# this watch() looks for all types of changes (CRUD)
# based on different CRUD operation a differnet callback can be used
def watch_db(callback):
    with collection.watch() as stream:
        while stream.alive:
            change = stream.try_next()
            # block until we get the change response
            if change is not None:
                # if change has occured trigger our custom call back
                callback(change["fullDocument"]["data"])
            # Sleep for a while before trying again to avoid flooding
            # the server with getMore requests
            time.sleep(5)


# create a thread so that the FASTAPI server can continue running without db watch blocking
thread = threading.Thread(target=watch_db, args=([on_data_change_callback]))
# Start the db watch process
thread.start()
