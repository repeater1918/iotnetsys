"""
AAS:
Watches mongoDB for update - decides when to send data to front-end - responds to front end requests

TODO:

1. Define schemas so AAS knows what type of document was inserted (send/rec/scmp etc.)
2. Based on front end requirments decide when and how to send updates to front-end
3. Add processing logic to calculation metrics 

"""
from pathlib import Path

from dotenv import load_dotenv

dotenv_path = Path(Path(__file__).parent.resolve(), "../.envs/mongodb.env")
load_dotenv(dotenv_path=dotenv_path)

import os
import threading
import time
from datetime import datetime
from typing import Dict, List
from collections import defaultdict
import requests, json
from database.mongodb import Database
from fastapi import FastAPI
from models import MetaStream, PacketStream, calculate_pdr_metrics, calculate_icmp_metrics, calculate_received_metrics, calculate_queue_loss, \
calculate_energy_cons_metrics
from models.e2e_delay import calculate_end_to_end_delay
from models.dead_loss import calculate_dead_loss

FRONT_END_URL = "http://127.0.0.1:8050/data-update"

# Connect to local mongo instance and define starting db = iotnetsys
client = Database(database_name="iotnetsys")

# Start FASTAPI server
app = FastAPI()

# Global reference variables to manage watchers
global response_history
response_history = 0
global update_event
update_event = datetime.now()
global packet_stream, meta_stream
packet_stream = PacketStream(packet_update_limit=100)
meta_stream = MetaStream(packet_update_limit=8)
global last_packet_id, last_meta_id
last_packet_id = last_meta_id = None
last_packet_ids = []
global network_df,node_df 
network_df = {} #this is storing dataframe for network level metric in format {"owner_metric": metric_dict}, example: {"pdr_metric": data}
node_df = defaultdict(dict) #this is storing dataframe for node level metric in format {"nodeid": {"owner_metric": metric_dict}}, example: {"1": {"pdr_metric": data}}

# Events (bools) to help prevent race conditions between metric and db watchers
is_updating_packet = threading.Event()
is_calculating_packet = threading.Event()
is_updating_meta = threading.Event()
is_calculating_meta = threading.Event()


# We will use these as API end points when the user changes parameters (via Dashboard)
@app.get("/")
async def root():
    return {"message": str(response_history)}


def packet_metric_scheduler():
    """
    Function runs perdically (~5sec) and checks if metric update is warranted
    based on the minimum number of new log packets required to trigger an update

    Provides a dataframe -> "df_all_packets" which provides all packet logs to date
    use this df to calculate your metrics

    """
    global packet_stream

    while True:
        if is_updating_packet.is_set():
            # print("PcktMetricScheduler: skip calc as db update is active")
            time.sleep(5)
            continue

        if not packet_stream.is_update_ready:
            # print("PcktMetricScheduler: skip calc not enough new packets")
            time.sleep(5)
            continue

        # Notify threads that metric calculation is in process
        is_calculating_packet.set()

        # This dataframe represents all historical packets
        df_all_packets = packet_stream.flush_stream().copy(deep=True)
        

        """ ########### Place calcs below here ########### """

        # Step 1 - using all historical packets (df_all_packets) - calculate your metrics and return a dataframe
        pdr_metric = calculate_pdr_metrics(df_all_packets, timeframe=60000, bins=10)
        
        # Step 2 - when you have the result convert your dataframe to a dictionary so it can be sent as json
        pdr_metric_dict = pdr_metric.to_dict("records")
        
        # Step 3 - add a label to your data so when it reaches the front end we know who it belongs to
        network_df['pdr_metric'] = pdr_metric_dict 

        # Nwe - to calculate end-to-end delay
        e2e_metric = calculate_end_to_end_delay(df_all_packets, timeframe=60000, bins=10)
        # convert dataframe to a dictionary so it can be sent as json
        e2e_dict = e2e_metric.to_dict("records")
        # adding a label to data so when it reaches the front end we know who it belongs to
        network_df['e2e_metric'] = e2e_dict
        # pass dictionary data into the on_packet_data_update to send it to the front-end

        # Nwe - to calculate dead loss
        deadloss_metric = calculate_dead_loss(df_all_packets, timeframe=60000, bins=10)
        # convert dataframe to a dictionary so it can be sent as json
        deadloss_dict = deadloss_metric.to_dict("records")
        # adding a label to data so when it reaches the front end we know who it belongs to
        network_df['deadloss_metric'] = deadloss_dict 
        # pass dictionary data into the on_packet_data_update to send it to the front-end

        received_metrics = calculate_received_metrics(df_all_packets, timeframe=20000, bins=10)
        received_metric_dict = received_metrics.to_dict("records")
        network_df['received_metric'] = received_metric_dict 

        for node in range(2,8):
            #TODO: change to dynamic node
            #Put your metric dict for node level here in below format
            #node_df[nodeid][owner_tag] = metric_dict (Example: nodedf[2]['pdr_metric'] = node2_pdr_metric_dict) 
            node_df[node]["pdr_metric"] = pdr_metric_dict 
            node_df[node]["e2e_metric"] = e2e_dict
            node_df[node]["deadloss_metric"] = deadloss_dict
            node_df[node]["received_metric"] = received_metric_dict
       
        """ ########### Place calcs above here ########### """

        # Notify threads metric calculation is complete (db updates can resume)
        is_calculating_packet.clear()

        time.sleep(5) 


def meta_metric_scheduler():
    """
    Function runs perdically (~30sec) and checks if metric update is warranted
    based on the minimum number of new meta packets required to trigger an update

    Provides a dataframe -> "df_all_meta_packets" which provides all meta logs to date
    use this df to calculate your metrics

    """

    global meta_stream

    while True:
        if is_updating_packet.is_set():
            # print("MetaMetricScheduler: skip calc as db update is active")
            time.sleep(15)
            continue

        if not meta_stream.is_update_ready:
            # print("MetaMetricScheduler: skip calc not enough new packets")
            time.sleep(30)
            continue

        # Notify threads that metric calculation is in process
        is_calculating_meta.set()

        # This dataframe represents all historical packets
        df_all_meta_packets = meta_stream.flush_stream().copy(deep=True)

        """ ########### Place calcs below here ########### """
        # Step 1 - using all historical packets (df_all_packets) - calculate your metrics and return a dataframe
        icmp_metric = calculate_icmp_metrics(df_all_meta_packets)
        # Step 2 - when you have the result convert your dataframe to a dictionary so it can be sent as json
        icmp_metric_dict = icmp_metric.to_dict("records")
        # Step 3 - add a label to your data so when it reaches the front end we know who it belongs to
        network_df['icmp_metric'] = icmp_metric_dict        

        queueloss_metrics = calculate_queue_loss(df_all_meta_packets)
        queueloss_metric_dict = queueloss_metrics.to_dict("records")
        network_df['queueloss_metric'] = icmp_metric_dict

        # Step 1 - using all historical packets (df_all_packets) - calculate your metrics and return a dataframe
        energy_cons_metric = calculate_energy_cons_metrics(df_all_meta_packets)
        # Step 2 - when you have the result convert your dataframe to a dictionary so it can be sent as json
        energy_metric_dict = energy_cons_metric.to_dict("records")
        # Step 3 - pass your dictionary data into the on_packet_data_update to send it to the front-end
        network_df['energy_cons_metric'] = energy_metric_dict

        for node in range(2,8):
            #TODO: change to dynamic node
            #Put your metric dict for node level here in below format
            #node_df[nodeid][owner_tag] = metric_dict (Example: nodedf[2]['pdr_metric'] = node2_pdr_metric_dict) 
            node_df[node]["icmp_metric"] = icmp_metric_dict 
            node_df[node]["queueloss_metric"] = queueloss_metric_dict
            node_df[node]["energy_cons_metric"] = energy_metric_dict
        
        """ ########### Place calcs above here ########### """


        # Notify threads metric calculation is complete (db updates can resume)
        is_calculating_meta.clear()

        time.sleep(15) 


def watch_packetlogs() -> None:
    """Periodically queries MongoDB to check for new packet logs and updates PacketStream"""
    while True:
        # if the metric calculation function (watch_metrics) is active, pause data update
        while is_calculating_packet.is_set():
            time.sleep(5)

        global last_packet_id, packet_stream, last_packet_ids

        # Notify threads data update is active
        is_updating_packet.set()

        # Query 1: Check the packetlog collection and get new document starting from last result
        data, id_max = client.find_by_pagination(
                collection_name="packetlogs", last_id=last_packet_id, page_size=100
            )
        
        if data is None:
            # print("WatchPcktLogs: no new packet logs in DB, putting watcher to sleep")
            is_updating_packet.clear()
            time.sleep(15)
            continue

        # Update the packet stream with new data
        packet_stream.append_stream(data)
        # Remember the latest document received for next query
        last_packet_id = id_max
        #print(data)
        # Notify threads data update is active
        is_updating_packet.clear()
        # print(
        #     f"WatchPcktLogs: stream size = {len(packet_stream.stream)}, all logs = {len(packet_stream.df_packet_hist)}, update ready: {packet_stream.is_update_ready}"
        # )
        time.sleep(5)


def watch_metalogs() -> None:
    """Periodically queries MongoDB to check for new meta logs and update MetaStream"""
    while True:
        # if the metric calculation function (watch_metrics) is active, pause data update
        while is_calculating_packet.is_set():
            time.sleep(15)

        global last_meta_id, meta_stream

        # Notify threads data update is active
        is_updating_meta.set()

        # Query 2: Check the metalog collection and get new document starting from last result
        data, id_max = client.find_by_pagination(
            collection_name="metalogs", last_id=last_meta_id, page_size=10
        )

        if data is None:
            # print("WatchMetaLogs: no new meta logs in DB, putting watcher to sleep")
            is_updating_packet.clear()
            time.sleep(30)
            continue

        # Update the meta stream with new data
        meta_stream.append_stream(data)
        # Remember the latest document received for next query
        last_meta_id = id_max

        # Notify threads data update is active
        is_updating_meta.clear()
        # print(
        #     f"WatchMetaLogs: stream size = {len(meta_stream.stream)}, all logs = {len(meta_stream.df_packet_hist)}, update ready: {meta_stream.is_update_ready}"
        # )
        time.sleep(15)


# This is called when a single view/graph data update is sent to front-end
# The Dash server is on localhost port 8050 for development
def send_data_to_front_end(response: List[Dict]):
    global response_history, update_event

    # store some stats for how many updates have happened and when last update occured
    update_time = datetime.now()
    seconds_since_last_update = (update_time - update_event).seconds
    # print(
    #     f"API POST: Sending data for [{response['owner']}] - last update: {seconds_since_last_update} seconds ago"
    # )
    response_history = response_history + 1
    response["update_count"] = response_history
    #print(response)
    #breakpoint()
    try:
        # send a post request to the Dash end point: http://127.0.0.1:8050/data-update
        req = requests.post(
            url=FRONT_END_URL, json=response
        )  # FIXME this may need to go into a thread/coroutine as it is blocking
    except requests.exceptions.Timeout as e:
        # connection made but request timed out
        # print(f"Timeout sending data to dash = {e}")
        pass
    except requests.exceptions.RequestException as e:
        # If the dash server is not running this error will typically trigger
        # print(f"Could not reach front-end - is server running? - {e}")
        pass

    update_event = datetime.now()


@app.get("/network_data/{metric_owner}")
async def read_network_df(metric_owner):
    response_df = network_df[metric_owner]
    return response_df


#Query format for nodelv: AAS_URI/nodelv_data/pdr_metric?node=2 
@app.get("/node_data/{metric_owner}")
async def read_node_df(metric_owner, node: int = 1):
    if node > 1:
        #node 1 is root already, no need to get it
        #print(f"API query for {node}")
        response_df = node_df[node][metric_owner]
        return response_df
    else: 
        return json.dumps({"success": False}), 200, {"ContentType": "application/json"}



# create a thread to run the packet log collection data fetch
packetlog_watch_thread = threading.Thread(target=watch_packetlogs)
metalog_watch_thread = threading.Thread(target=watch_metalogs)

# create a thread so that the FASTAPI server can continue running without db watch blocking
packet_scheduler_thread = threading.Thread(target=packet_metric_scheduler)
meta_scheduler_watch_thread = threading.Thread(target=meta_metric_scheduler)

# start db watchers
packetlog_watch_thread.start()
metalog_watch_thread.start()

# start metric schedulers
packet_scheduler_thread.start()
meta_scheduler_watch_thread.start()
