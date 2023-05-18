"""
AAS:
Watches mongoDB for update - decides when to send data to front-end - responds to front end requests

"""
import os
from pathlib import Path

from dotenv import load_dotenv

if os.environ.get('DEPLOYMENT', 'dev') == 'dev':
    dotenv_path_dev = Path(Path(__file__).parent.resolve(), "../.envs/mongodb.env")
    load_dotenv(dotenv_path=dotenv_path_dev)

print(f"Running in mode -> {os.environ.get('DEPLOYMENT', 'dev')}")

import copy
import sys
import threading
import time
from collections import defaultdict
from typing import Union
from datetime import datetime
from database.mongodb import Database
from fastapi import FastAPI, HTTPException
from metrics_calculators import (calculate_dead_loss,
                                 calculate_end_to_end_delay,
                                 calculate_energy_cons_metrics,
                                 calculate_icmp_metrics,
                                 calculate_parent_change_ntwk_metrics,
                                 calculate_pdr_metrics, calculate_queue_loss,
                                 calculate_received_metrics, topology_df_gen)
from models import MetaStream, PacketStream, Timeframe, TopologyStream, SessionID

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
global packet_stream, meta_stream, topo_stream
packet_stream = PacketStream(packet_update_limit=20)
meta_stream = MetaStream(packet_update_limit=1)
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
global network_df,node_df,topo_df, topo_dict
network_df = {} #this is storing dataframe for network level metric in format {"owner_metric": metric_dict}, example: {"pdr_metric": data}
node_df = defaultdict(dict) #this is storing dataframe for node level metric in format {"nodeid": {"owner_metric": metric_dict}}, example: {"1": {"pdr_metric": data}}
topo_df = {}
topo_dict = {}

# Events (bools) to help prevent race conditions between metric and db watchers
is_updating_packet = threading.Event()
is_calculating_packet = threading.Event()
is_updating_meta = threading.Event()
is_calculating_meta = threading.Event()
is_updating_topo = threading.Event()
is_calculating_topo = threading.Event()


# API end points for user initiated changes to parameters (via Dashboard)
@app.get("/")
async def root():
    return {"network_df": sys.getsizeof(network_df), "node_df": sys.getsizeof(node_df)}

@app.post("/api/timeframe")
async def root(data: Timeframe):
    global timeframe_param 
    timeframe_param = data.timeframe
    packet_stream.is_update_ready = True    
    meta_stream.is_update_ready = True
    print(data.timeframe)

@app.post("/api/timeframe_dls")
async def root(data: Timeframe):
    global timeframe_dls 
    timeframe_dls = data.timeframe
    packet_stream.is_update_ready = True
    meta_stream.is_update_ready = True
    print(data.timeframe)


def packet_metric_scheduler():
    """
    Function runs periodical (~5sec) and checks if metric update is warranted
    based on the minimum number of new log packets required to trigger an update

    Provides a dataframe -> "df_all_packets" which provides all packet logs to date
    use this df to calculate your metrics

    """
    global packet_stream, node_df
    global timeframe_param,timeframe_dls

    while True:
        if is_updating_packet.is_set():
            # print("PcktMetricScheduler: skip calc as db update is active")
            time.sleep(0.1)
            continue

        if not packet_stream.is_update_ready:
            # print("PcktMetricScheduler: skip calc not enough new packets")
            time.sleep(.1)
            continue

        # Notify threads that metric calculation is in process
        is_calculating_packet.set()

        # This dataframe represents all historical packets
        df_all_packets = packet_stream.flush_stream().copy(deep=True)
        user_data_dict = {"data_timeframe": timeframe_param, "deadline_timeframe": timeframe_dls, "sessionid": sessionid}
        """ ########### Place calcs below here ########### """
        try:
            pdr_metric_dict, pdr_node_metric_dict = calculate_pdr_metrics(copy.deepcopy(df_all_packets), timeframe=timeframe_param*1000, bins=10)
            network_df['pdr_metric'] = pdr_metric_dict + [user_data_dict]
            for node, data in pdr_node_metric_dict.items():
                node_df[node]['pdr_metric'] = data + [user_data_dict]
        except Exception as ex:
            print(f'Error in PDR METRIC calc: {ex}')    
        
        try:
            # Nwe - to calculate end-to-end delay (network level)
            e2e_metric, e2e_node_metric = calculate_end_to_end_delay(copy.deepcopy(df_all_packets), timeframe=timeframe_param*1000, bins=10)
            network_df['e2e_metric'] = e2e_metric + [user_data_dict]
            # Nwe - to calculate end-to-end delay (node level)
            for node,data in e2e_node_metric.items():
                node_df[node]['e2e_metric'] = data + [user_data_dict]
        except Exception as ex:
            print(f'Error in E2E METRIC calc: {ex}')        

        try:
            # Nwe - to calculate dead loss (network level)
            deadloss_metric, dloss_node_metric = calculate_dead_loss(copy.deepcopy(df_all_packets), timeframe=timeframe_param*1000, timeframe_deadline=timeframe_dls, bins=10)
            network_df['deadloss_metric'] = deadloss_metric+ [user_data_dict]
            # Nwe - to calculate dead loss (node level)
            for node, data in dloss_node_metric.items():
                node_df[node]['deadloss_metric'] = data + [user_data_dict]
        except Exception as ex:
            print(f'Error in DEADLINE LOSS METRIC calc: {ex}')        

        try:
            #calculate number of received packets
            received_metrics = calculate_received_metrics(copy.deepcopy(df_all_packets), timeframe=timeframe_param*1000, bins=10)        
            #for network
            network_df['received_metric'] = received_metrics  + [user_data_dict]
            #for nodes
            #for node, data in received_metrics_node.items():
            #     node_df[node]['received_metric'] = data
        except Exception as ex:
            print(f'Error in RECV PACKETS METRIC calc: {ex}')    
      
        """ ########### Place calcs above here ########### """

        # Add timeframe & deadline loss to track which data used to calculate metrics
        #print(f"Packet metric calculated using this param data {timeframe_param}; deadline {timeframe_dls}; session {sessionid}")        
        # Notify threads metric calculation is complete (db updates can resume)
        is_calculating_packet.clear()

        time.sleep(.1) 


def meta_metric_scheduler():
    """
    Function runs periodically and checks if metric update is warranted
    based on the minimum number of new meta packets required to trigger an update

    Provides a dataframe -> "df_all_meta_packets" which provides all meta logs to date
    use this df to calculate your metrics

    """

    global meta_stream
    global timeframe_param,timeframe_dls


    while True:
        if is_updating_meta.is_set():
            # print("MetaMetricScheduler: skip calc as db update is active")
            time.sleep(0.5)
            continue

        if not meta_stream.is_update_ready:
            # print("MetaMetricScheduler: skip calc not enough new packets")
            time.sleep(0.5)
            continue

        # Notify threads that metric calculation is in process
        is_calculating_meta.set()

        # This dataframe represents all historical packets
        df_all_meta_packets = meta_stream.flush_stream().copy(deep=True)
        user_data_dict = {"data_timeframe": timeframe_param, "deadline_timeframe": timeframe_dls, "sessionid": sessionid}
        """ ########### Place calcs below here ########### """
        try:
            # Step 1 + 2 - using all historical packets (df_all_packets) - calculate your metrics and return a dataframe
            net_icmp_metric, node_icmp_metric = calculate_icmp_metrics(copy.deepcopy(df_all_meta_packets))
               
            # Step 3 - add a label to your data so when it reaches the front end we know who it belongs to
            network_df['icmp_metric'] = net_icmp_metric + [user_data_dict]   
            #Step 4 - Calculate metric for specific node
            for node, data in node_icmp_metric.items():
                node_df[node]['icmp_metric'] = data + [user_data_dict]   
        except Exception as ex:
            print(f'Error in ICMP METRIC calc: {ex}')

        try:        
            #calculate queue loss
            queueloss_network, queueloss_node = calculate_queue_loss(copy.deepcopy(df_all_meta_packets))
            #for network
            network_df['queueloss_metric'] = queueloss_network + [user_data_dict]   
            #for each node
            for node, data in queueloss_node.items():
                node_df[node]['queueloss_metric'] = data + [user_data_dict]   
        except Exception as ex:
            print(f'Error in QUEUE LOSS METRIC calc: {ex}')

        try:    
            # Step 1 - using all historical packets (df_all_packets) - to calculate energy consumption metrics and return a dataframe
            energy_cons_metric, node_energy_cons = calculate_energy_cons_metrics(copy.deepcopy(df_all_meta_packets))
            # Step 3 - Passing dictionary data into the on_packet_data_update to send it to the front-end
            network_df['energy_cons_metric'] = energy_cons_metric+ [user_data_dict]   
            for node, data in node_energy_cons.items():
                node_df[node]['energy_cons_metric'] = data + [user_data_dict]   
            
            #Step 4 - Calculate metric for specific node
           
        except Exception as ex:
            print(f'Error in ENERGY CONS METRIC calc: {ex}')

        try:           
            pc_metric_network_int, node_pc_metric = calculate_parent_change_ntwk_metrics(copy.deepcopy(df_all_meta_packets))
            # Step 3 - add a label to your data so when it reaches the front end we know who it belongs to
            network_df['pc_metric'] = pc_metric_network_int + [user_data_dict]   
            #Step 4 - Calculate metric for specific node
            for node, data in node_pc_metric.items():
                node_df[node]['pc_metric'] = data + [user_data_dict]   
            
        except Exception as ex:
            print(f'Error in PC METRIC calc: {ex}')       
        """ ########### Place calcs above here ########### """
        #print(f"Meta metric calculated with this param {sessionid}") 
        network_df['user_data'] = {"data_timeframe": timeframe_param, "deadline_timeframe": timeframe_dls, "sessionid": sessionid}
        node_df['user_data'] = {"data_timeframe": timeframe_param, "deadline_timeframe": timeframe_dls, "sessionid": sessionid}
                
        # Notify threads metric calculation is complete (db updates can resume)
        is_calculating_meta.clear()

        time.sleep(1) 

def topology_event_scheduler():
    """
    Function runs periodically and checks if metric update is warranted
    based on the minimum number of new topo packets required to trigger an update

    Provides a dataframe -> "df_all_topo_packets" which provides all topo logs to date
    use this df to calculate your metrics

    """
    global topo_df, topo_dict,timeframe_param,timeframe_dls, topo_dict
    while True:
        if is_updating_topo.is_set():
            #print("TopoEventScheduler: skip calc as db update is active")
            time.sleep(0.5)
            continue

        if not topo_stream.is_update_ready:
            #print("TopoEventScheduler: skip calc not enough new packets")
            time.sleep(0.5)
            continue
        
        # Notify threads that metric calculation is in process
        is_calculating_topo.set()

        # This dataframe represents all historical packets
        df_all_topo_packets = topo_stream.flush_stream().copy(deep=True)
        try:
            topo_df = topology_df_gen(copy.deepcopy(df_all_topo_packets))
            topo_df= topo_df.to_dict('records')
        except Exception as ex:
            print(f"Error in topology df: {ex}")
        # Notify threads metric calculation is complete (db updates can resume)
        #print(f"Topology calculated with this param {sessionid}")
        topo_dict['user_data'] = {"sessionid": sessionid}
        is_calculating_topo.clear()

        time.sleep(1) 



def watch_packetlogs() -> None:
    """Periodically queries MongoDB to check for new packet logs and updates PacketStream"""
    while True:
        # if the metric calculation function (watch_metrics) is active, pause data update
        while is_calculating_packet.is_set():
            time.sleep(0.2)

        global last_packet_id, packet_stream, sessionid

        # Notify threads data update is active
        is_updating_packet.set()

        # Query 1: Check the packetlogs for each node collection and get new document starting from last result
        data_list = []
        for name in node_collection_names:

            data, id_max= client.find_by_pagination(
                collection_name=name, last_id=last_packet_id.get(name), page_size=1000, sessionid=sessionid
            )
            data_list.append(data)
            if id_max != None:
                #if id_max is none, don't re-assign (it makes last_packet_id points to beginning again)
                last_packet_id[name] = id_max

        # Exclude None results
        data_list = [item for item in data_list if item != None]

        if len(data_list) == 0:
            # print("WatchPcktLogs: no new packet logs in DB, putting watcher to sleep")
            is_updating_packet.clear()
            time.sleep(1)
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
        time.sleep(0.3)


def watch_metalogs() -> None:
    """Periodically queries MongoDB to check for new meta logs and update MetaStream"""
    while True:
        # if the metric calculation function (watch_metrics) is active, pause data update
        while is_calculating_meta.is_set():
            time.sleep(0.5)

        global last_meta_id, meta_stream, sessionid

        # Notify threads data update is active
        is_updating_meta.set()
        
        # Query 2: Check the metalog collection and get new document starting from last result
        data, id_max = client.find_by_pagination(
            collection_name="metalogs", last_id=last_meta_id, page_size=100, sessionid=sessionid
        )

        if data is None:
            # print("WatchMetaLogs: no new meta logs in DB, putting watcher to sleep")
            is_updating_meta.clear()
            time.sleep(1)
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
        time.sleep(0.5)


def watch_topology() -> None:
    """Periodically queries MongoDB to check for new typology changes """ 
    while True:

        while is_calculating_topo.is_set():
            time.sleep(0.5)

        global last_topo_id, topo_stream
        is_updating_topo.set()

        #print("Topology data update in progress")
        global sessionid
        if sessionid == None:
            sessionid = client.find_session_id(collection_name="topology")[-1]    
            last_topo_id = None
        data, id_max = client.find_by_pagination(
            collection_name="topology", last_id = last_topo_id, page_size=50, sessionid=sessionid
        )

        if data is None:
            #print("WatchTopoLogs: no new topo logs in DB, putting watcher to sleep")
            is_updating_topo.clear()
            time.sleep(1)
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
        time.sleep(0.5)


@app.get("/api/networkmetric/{metric_owner}")
async def read_network_df(metric_owner):
    """API GET to return calculated network metric dataframe"""
    try:
        if (network_df[metric_owner][-1]['data_timeframe'] == timeframe_param) and (network_df[metric_owner][-1]['deadline_timeframe'] == timeframe_dls) and \
        (network_df[metric_owner][-1]['sessionid'] == sessionid):
            
            response_df = network_df[metric_owner][:-1]
        else:
            raise Exception("Calculated dataframe is not using current UI timeframe & dl")
        
    except Exception as e:
        print(f"API node data call has exception {e}")
        response_df = {}
        raise HTTPException(status_code=404, detail="Item not found")
        
    return response_df


#Query format for nodelv: AAS_URI/nodelv_data/pdr_metric?node=2 
@app.get("/api/nodemetric/{metric_owner}")
async def read_node_df(metric_owner, node: int = 1):
    """API GET to return calculated node metric dataframe"""
    response_df = {}
    if node > 0:
        #node 1 is root already, no need to get it
        #print(f"API query for {node}")
        try:
            if (node_df[node][metric_owner][-1]['data_timeframe'] == timeframe_param) and (node_df[node][metric_owner][-1]['deadline_timeframe'] == timeframe_dls) and \
                (node_df[node][metric_owner][-1]['sessionid'] == sessionid):
                response_df = node_df[node][metric_owner][:-1]
                return response_df
            else:
               raise Exception("Calculated dataframe is not using current UI timeframe & dl")

        except Exception as e:
            print(f"API node data call has exception {e}")
            response_df = {}
            raise HTTPException(status_code=404, detail="Item not found")
    
    return response_df


@app.get("/api/topodata/")
async def read_topo_db(q: Union[str, None] = None):
    """API GET to return calculated topology dataframe"""
    supported_query = ['node_sensor', 'node_parent']
    try:
        if (topo_dict['user_data']['sessionid'] == sessionid):
            if q in supported_query:
                if q == 'node_sensor':
                    res = [{"node": x['node'], "hop_count":x['hop_count']} for x in topo_df if x['role'] == 'sensor']          
                if q == 'node_parent':
                    res = [x['node'] for x in topo_df if x['role'] == 'server']
            else:
                res = topo_df    
        else:
            raise Exception("Calculated dataframe is not using current UI timeframe & dl")
    except Exception as e:
        print(f"API topodata has exception {e}")
        res = []
        raise HTTPException(status_code=404, detail="Item not found")

    if len(res) == 0:
        print("No topology data")
    return res


@app.get("/api/sessiondata")
async def read_session_data(q: Union[str, None] = None):
    """API GET to return list of session/experiments"""
    if q == 'current':
        global sessionid
        res = sessionid
    else:
        res = client.find_session_id(collection_name='topology')
        res = {"sessionid": res}
    return res


@app.post("/api/sessiondata")
async def post_session_data(data: SessionID):
    """Receive new sessionid from UI and delete previous df, default: sessionid is the latest"""
    global sessionid, last_meta_id, last_packet_id, last_topo_id, topo_dict

    try:
        sessionid_dt = datetime.fromisoformat(data.sessionid)
    except:
        sessionid_dt = client.find_session_id(collection_name="topology")[-1]  
    if sessionid_dt != sessionid:
        print(f"All data frames are reset because mismatch between POST session: {sessionid_dt} and AAS session: {sessionid}")
        meta_stream.delete_df()
        packet_stream.delete_df()
        topo_stream.delete_df()
        topo_dict.clear(); network_df.clear(); node_df.clear()
        last_meta_id = None
        last_packet_id.clear()
        last_topo_id = None
        sessionid = sessionid_dt  
        if sessionid_dt != '':
           sessionid = copy.deepcopy(sessionid_dt)
        else:
            sessionid = client.find_session_id(collection_name="topology")[-1]   
        time.sleep(2) #block the dashboard loading output for 2s to wait metric to calculate 

    return sessionid


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
