import requests
import os
from datetime import timedelta, datetime
AAS_URI = os.environ.get('AAS_URI', "http://127.0.0.1:8000/api/") #AAS supports networklv_data or nodelv_data
print(f"AAS_URI -> {AAS_URI}")

global supported_metrics, node_supported_metrics
common_supported_metrics = ["pdr_metric","icmp_metric","e2e_metric", "deadloss_metric", "queueloss_metric","energy_cons_metric"]
node_supported_metrics = [*common_supported_metrics, "pc_metric"]
network_supported_metrics = [*common_supported_metrics, "received_metric"]

def get_network_data(metric = None):
    """Request API to get network metrics"""
    result_dict = {}
    
    for v in network_supported_metrics:
        if metric != None and v != metric: 
            continue
        res = requests.get(AAS_URI+f"networkmetric/{v}")
        if res.status_code == 200:
            res = res.json()
        else:
            res = []
        
        result_dict[v] = res
    #print ("Cache updated at ", datetime.now())
    return result_dict


def get_node_data(nodeid, metric=None):
    """Request API to get node metrics"""
    result_dict = {}    
    
    #loop through all metric
    for v in node_supported_metrics:
        if metric != None and v != metric: 
            continue          
        res = requests.get(AAS_URI+f"nodemetric/{v}?node={nodeid}") 
        if res.status_code == 200:
            res = res.json()
        else:
            res = []
        result_dict[v] = res
    #print ("Cache updated at ", datetime.now())
    return result_dict


def get_topo_data(query = None):
    """Request API to get network topology data"""
    res = requests.get(AAS_URI+f"topodata/?q={query}")
    if res.status_code == 200:
        res = res.json()
    else:
        res = []
    return res

def get_session_data():
    """Request API to get session/network run history """
    res = requests.get(AAS_URI+f"sessiondata")
    if res.status_code == 200:
        res = res.json()        
    else:
        res = []
        
    return res

def send_timeframe(milliseconds: int):
    """POST API to update timeframe"""
    result_dict = {'timeframe': milliseconds}
    res = requests.post(AAS_URI+f"timeframe", json=result_dict) 
    #print(f"Timeframe API call status: {res.status_code}")
    return res
    # TODO error management

def send_dlloss(milliseconds: int):
    """POST API to update deadline loss"""
    result_dict = {'timeframe': milliseconds}
    res = requests.post(AAS_URI+f"timeframe_dls", json=result_dict) 
    #print(f"Dloss API call status: {res.status_code}")
    return res
    # TODO error management

def send_sessionid(sessionid: str, ui_tz: int = 0):
    """POST API to update sessionid """
    
    if ui_tz != 0 and sessionid != '':
        sessionid_dt = datetime.fromisoformat(sessionid)        
        sessionid_dt = sessionid_dt + timedelta(minutes=ui_tz)
        sessionid = datetime.isoformat(sessionid_dt)

    result_dict = {"sessionid": sessionid}
    res = requests.post(AAS_URI+f"sessiondata", json=result_dict) 
    res = res.json()
    return res
        