"""
AAS:
Watches mongoDB for update - decides when to send data to front-end - responds to front end requests

TODO:

1. Define schemas so AAS knows what type of document was inserted (send/rec/scmp etc.)
2. Based on front end requirments decide when and how to send updates to front-end
3. Add processing logic to calculation metrics 

"""
from pathlib import Path
import os
from dotenv import load_dotenv

if os.environ.get('DEPLOYMENT', 'dev') == 'dev':
    dotenv_path_dev = Path(Path(__file__).parent.resolve(), "../.envs/mongodb.env")
    load_dotenv(dotenv_path=dotenv_path_dev)

print(f"Running in mode -> {os.environ.get('DEPLOYMENT', 'dev')}")

import sys
import pandas as pd
import threading
import time
from datetime import datetime
from typing import Dict, List, Union
import copy
from collections import defaultdict
import requests, json
from database.mongodb import Database
from fastapi import FastAPI
from models import MetaStream, PacketStream,TopologyStream
from metrics_calculators import calculate_pdr_metrics, calculate_icmp_metrics, \
    calculate_parent_change_ntwk_metrics, calculate_parent_change_node_metrics, calculate_received_metrics, calculate_queue_loss, \
calculate_energy_cons_metrics,calculate_end_to_end_delay, calculate_dead_loss, topology_df_gen
from models import Timeframe

FRONT_END_URL = "http://127.0.0.1:8050/data-update"

# Connect to local mongo instance and define starting db = iotnetsys
client = Database(database_name="iotnetsys")
node_collection_names = client.get_node_collection_names()

# Start FASTAPI server
app = FastAPI()

#  time frame parameter and deadline loss limit
global timeframe_param, timeframe_dls
timeframe_param=60
timeframe_dls = 60
# Global reference variables to manage watchers
global response_history
response_history = 0
global update_event
update_event = datetime.now()
global packet_stream, meta_stream, topo_stream
packet_stream = PacketStream(packet_update_limit=100)
meta_stream = MetaStream(packet_update_limit=8)
topo_stream = TopologyStream(packet_update_limit=1)

#latest id in database to determine pointer
global last_packet_id, last_meta_id, last_topo_id
last_meta_id = None
last_packet_id = {}
last_topo_id = None

#global session id to determine which run data is used
global sessionid
sessionid = None

#global dictionary to store calculated value
global network_df,node_df,topo_df
network_df = {} #this is storing dataframe for network level metric in format {"owner_metric": metric_dict}, example: {"pdr_metric": data}
node_df = defaultdict(dict) #this is storing dataframe for node level metric in format {"nodeid": {"owner_metric": metric_dict}}, example: {"1": {"pdr_metric": data}}
topo_df = {}

# Events (bools) to help prevent race conditions between metric and db watchers
is_updating_packet = threading.Event()
is_calculating_packet = threading.Event()
is_updating_meta = threading.Event()
is_calculating_meta = threading.Event()
is_updating_topo = threading.Event()
is_calculating_topo = threading.Event()


# We will use these as API end points when the user changes parameters (via Dashboard)
@app.get("/")
async def root():
    return {"network_df": sys.getsizeof(network_df), "node_df": sys.getsizeof(node_df)}

@app.post("/api/timeframe")
async def root(data: Timeframe):
    global timeframe_param 
    timeframe_param = data.timeframe
    print(data.timeframe)

@app.post("/api/timeframe_dls")
async def root(data: Timeframe):
    global timeframe_dls 
    timeframe_dls = data.timeframe
    print(data.timeframe)


def packet_metric_scheduler():
    """
    Function runs perdically (~5sec) and checks if metric update is warranted
    based on the minimum number of new log packets required to trigger an update

    Provides a dataframe -> "df_all_packets" which provides all packet logs to date
    use this df to calculate your metrics

    """
    global packet_stream, node_df
    global timeframe_param,timeframe_dls

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

        try:
            pdr_metric_dict, pdr_node_metric_dict = calculate_pdr_metrics(copy.deepcopy(df_all_packets), timeframe=60000, bins=10)
            network_df['pdr_metric'] = pdr_metric_dict 
            for node, data in pdr_node_metric_dict.items():
                node_df[node]['pdr_metric'] = data
        except Exception as ex:
            print(f'Error in PDR METRIC calc: {ex}')    

        # Nwe - to calculate end-to-end delay (network level)
        try:
            e2e_metric = calculate_end_to_end_delay(copy.deepcopy(df_all_packets), timeframe=timeframe_param*1000, bins=10,nodeID=-1)
            e2e_dict = e2e_metric.to_dict("records")
            network_df['e2e_metric'] = e2e_dict
            # Nwe - to calculate end-to-end delay (node level)
            for node in range(2,8):
                e2e_node_metric = calculate_end_to_end_delay(copy.deepcopy(df_all_packets), timeframe=timeframe_param*1000, bins=10,nodeID=node)
                e2e_node_metric_dict = e2e_node_metric.to_dict("records")
                node_df[node]['e2e_metric'] = e2e_node_metric_dict
        except Exception as ex:
            print(f'Error in E2E METRIC calc: {ex}')        

        try:
            # Nwe - to calculate dead loss (network level)
            #Dang - temp fix for dl loss below, need to correct it before deployment
            deadloss_metric = calculate_dead_loss(copy.deepcopy(df_all_packets), timeframe=timeframe_param*1000, timeframe_deadline=timeframe_dls*1000, bins=10,nodeID=-1)
            deadloss_dict = deadloss_metric.to_dict("records")
            network_df['deadloss_metric'] = deadloss_dict 
            # Nwe - to calculate dead loss (node level)
            for node in range(2,8):
                deadloss_node_metric = calculate_dead_loss(copy.deepcopy(df_all_packets), timeframe=timeframe_param*1000,timeframe_deadline=timeframe_dls*1000,bins=10,nodeID=node)
                deadloss_node_metric_dict = deadloss_node_metric.to_dict("records")
                node_df[node]['deadloss_metric'] = deadloss_node_metric_dict
        except Exception as ex:
            print(f'Error in DEADLINE LOSS METRIC calc: {ex}')        

        try:
            #calculate number of received packets
            received_metrics, received_metrics_node = calculate_received_metrics(copy.deepcopy(df_all_packets), timeframe=timeframe_param*1000, bins=10)        
            #for network
            network_df['received_metric'] = received_metrics 
            #for nodes
            for node, data in received_metrics_node.items():
                node_df[node]['received_metric'] = data
        except Exception as ex:
            print(f'Error in RECV PACKETS METRIC calc: {ex}')    

        try:
            pc_metric_network_int = calculate_parent_change_ntwk_metrics(df_all_packets, timeframe=60000, bins=10)
            pc_metric_node = calculate_parent_change_node_metrics(df_all_packets, timeframe=60000, bins=10) #pc_metric is not working, with 0 in values ..
            network_df["pc_metric_network"] = pc_metric_network_int
            # Step 2 - when you have the result convert your dataframe to a dictionary so it can be sent as json
            pc_metric_node_dict = pc_metric_node.to_dict("records")
        except Exception as ex:
            print(f'Error in PC METRIC calc: {ex}')       

       
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
        try:
            # Step 1 + 2 - using all historical packets (df_all_packets) - calculate your metrics and return a dataframe
            net_icmp_metric, node_icmp_metric = calculate_icmp_metrics(copy.deepcopy(df_all_meta_packets))
            # Step 3 - add a label to your data so when it reaches the front end we know who it belongs to
            network_df['icmp_metric'] = net_icmp_metric        
            #Step 4 - Calculate metric for specific node
            for node, data in node_icmp_metric.items():
                node_df[node]['icmp_metric'] = data
        except Exception as ex:
            print(f'Error in ICMP METRIC calc: {ex}')

        try:        
            #calculate queue loss
            queueloss_network, queueloss_node = calculate_queue_loss(copy.deepcopy(df_all_meta_packets))
            #for network
            network_df['queueloss_metric'] = queueloss_network
            #for each node
            for node, data in queueloss_node.items():
                node_df[node]['queueloss_metric'] = data
        except Exception as ex:
            print(f'Error in QUEUE LOSS METRIC calc: {ex}')

        try:    
            # Step 1 - using all historical packets (df_all_packets) - calculate your metrics and return a dataframe
            energy_cons_metric = calculate_energy_cons_metrics(copy.deepcopy(df_all_meta_packets))
            # Step 2 - when you have the result convert your dataframe to a dictionary so it can be sent as json
            energy_metric_dict = energy_cons_metric.to_dict("records")
            # Step 3 - pass your dictionary data into the on_packet_data_update to send it to the front-end
            network_df['energy_cons_metric'] = energy_metric_dict

            #Step 4 - Calculate metric for specific node
            for node in range(2,8):
                energy_node = df_all_meta_packets.loc[df_all_meta_packets['node']==node].copy()
                energy_cons_node_metrics = calculate_energy_cons_metrics(energy_node)
                energy_cons_node_metrics_dict = energy_cons_node_metrics.to_dict("records")
                node_df[node]['energy_cons_metric'] = energy_cons_node_metrics_dict 
        except Exception as ex:
            print(f'Error in ENERGY CONS METRIC calc: {ex}')

        
        """ ########### Place calcs above here ########### """


        # Notify threads metric calculation is complete (db updates can resume)
        is_calculating_meta.clear()

        time.sleep(15) 

def topology_event_scheduler():
     
     global topo_df
     while True:
        if is_updating_topo.is_set():
            #print("TopoEventScheduler: skip calc as db update is active")
            time.sleep(15)
            continue

        if not topo_stream.is_update_ready:
            #print("TopoEventScheduler: skip calc not enough new packets")
            time.sleep(30)
            continue
        
        # Notify threads that metric calculation is in process
        is_calculating_topo.set()

        # This dataframe represents all historical packets
        df_all_topo_packets = topo_stream.flush_stream().copy(deep=True)

        topo_df = topology_df_gen(copy.deepcopy(df_all_topo_packets))
        topo_df = topo_df.to_dict('records')

        # Notify threads metric calculation is complete (db updates can resume)
        df_all_topo_packets =None #clear computed
        is_calculating_topo.clear()

        time.sleep(15) 



def watch_packetlogs() -> None:
    """Periodically queries MongoDB to check for new packet logs and updates PacketStream"""
    while True:
        # if the metric calculation function (watch_metrics) is active, pause data update
        while is_calculating_packet.is_set():
            time.sleep(5)

        global last_packet_id, packet_stream, sessionid

        # Notify threads data update is active
        is_updating_packet.set()

        # Query 1: Check the packetlogs for each node collection and get new document starting from last result
        data_list = []
        for name in node_collection_names:

            data, id_max= client.find_by_pagination(
                collection_name=name, last_id=last_packet_id.get(name), page_size=10, sessionid=sessionid
            )
            data_list.append(data)
            if id_max != None:
                #if id_max is none, don't re-assign (it makes last_packet_id points to begining again)
                last_packet_id[name] = id_max

        # Exclude None results
        data_list = [item for item in data_list if item != None]

        if len(data_list) == 0:
            # print("WatchPcktLogs: no new packet logs in DB, putting watcher to sleep")
            is_updating_packet.clear()
            time.sleep(15)
            continue

        # Unwrap list of list node resuls
        data = [node for lst in data_list for node in lst] 
        # Update the packet stream with new data
        packet_stream.append_stream(data)
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
        while is_calculating_meta.is_set():
            time.sleep(15)

        global last_meta_id, meta_stream, sessionid

        # Notify threads data update is active
        is_updating_meta.set()
        
        # Query 2: Check the metalog collection and get new document starting from last result
        data, id_max = client.find_by_pagination(
            collection_name="metalogs", last_id=last_meta_id, page_size=10, sessionid=sessionid
        )

        if data is None:
            # print("WatchMetaLogs: no new meta logs in DB, putting watcher to sleep")
            is_updating_meta.clear()
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


def watch_topology() -> None:
    while True:

        while is_calculating_topo.is_set():
            time.sleep(15)

        global last_topo_id, topo_stream
        is_updating_topo.set()

        #print("Topology data update in progress")
        global sessionid
        sessionid = client.find_by_session(collection_name="topology", sessionid=None)

        data, id_max = client.find_by_pagination(
            collection_name="topology", last_id = None, page_size=10, sessionid=sessionid
        )

        if data is None:
            # print("WatchMetaLogs: no new topo logs in DB, putting watcher to sleep")
            is_updating_topo.clear()
            time.sleep(30)
            continue

        # Update the meta stream with new data
        topo_stream.append_stream(data)
        # Remember the latest document received for next query
        last_topo_id = id_max

        # Notify threads data update is active
        is_updating_topo.clear()
        # print(
        #     f"WatchTopoLogs: stream size = {len(meta_stream.stream)}, all logs = {len(meta_stream.df_packet_hist)}, update ready: {meta_stream.is_update_ready}"
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
    try:
        response_df = network_df[metric_owner]
    except:
        response_df = {}
        
    return response_df


#Query format for nodelv: AAS_URI/nodelv_data/pdr_metric?node=2 
@app.get("/node_data/{metric_owner}")
async def read_node_df(metric_owner, node: int = 1):
    global node_df
    response_df = {}
    if node > 1:
        #node 1 is root already, no need to get it
        #print(f"API query for {node}")
        try:
            response_df = node_df[node][metric_owner]
            return response_df
        except Exception as e:
            print(e)
            response_df = {}
    
    return response_df


@app.get("/topo_data/")
async def read_topo_db(q: Union[str, None] = None):
    supported_query = ['node_sensor', 'node_parent']
    
    if q in supported_query:
        if q == 'node_sensor':
            res = [x['node'] for x in topo_df if x['role'] == 'sensor']          
        if q == 'node_parent':
            res = [x['node'] for x in topo_df if x['role'] == 'server']
    else:
        res = topo_df

    return res


# create a thread to run the packet log collection data fetch
packetlog_watch_thread = threading.Thread(target=watch_packetlogs)
metalog_watch_thread = threading.Thread(target=watch_metalogs)
topology_watch_thread = threading.Thread(target=watch_topology)

# create a thread so that the FASTAPI server can continue running without db watch blocking
packet_scheduler_thread = threading.Thread(target=packet_metric_scheduler)
meta_scheduler_watch_thread = threading.Thread(target=meta_metric_scheduler)
topo_scheduler_thread = threading.Thread(target=topology_event_scheduler)

# start db watchers
topology_watch_thread.start() #topology is initiated first to identify session use
packetlog_watch_thread.start()
metalog_watch_thread.start()


# start metric schedulers
topo_scheduler_thread.start()
packet_scheduler_thread.start()
meta_scheduler_watch_thread.start()

