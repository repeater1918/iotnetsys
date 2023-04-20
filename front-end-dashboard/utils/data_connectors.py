import requests
import os

AAS_URI = os.environ.get('AAS_URI', "http://127.0.0.1:8000/") #AAS supports networklv_data or nodelv_data
print(f"AAS_URI -> {os.environ.get('AAS_URI', 'http://127.0.0.1:8000/')}")

global supported_metrics
supported_metrics = ["pdr_metric","icmp_metric","received_metric", "e2e_metric", "deadloss_metric", "queueloss_metric","energy_cons_metric"]
node_supported_metrics = [*supported_metrics, "pc_metric_node"]

def get_network_data():
    result_dict = {}
    for v in supported_metrics:
        res = requests.get(AAS_URI+f"network_data/{v}")
        if res.status_code == 200:
            res = res.json()
        else:
            res = []
        
        result_dict[v] = res
    #print ("Cache updated at ", datetime.now())
    return result_dict


def get_node_data(nodeid):
    result_dict = {}
    for v in node_supported_metrics:
        res = requests.get(AAS_URI+f"node_data/{v}?node={nodeid}") 
        if res.status_code == 200:
            res = res.json()
        else:
            res = []
        result_dict[v] = res
    #print ("Cache updated at ", datetime.now())
    return result_dict

def send_timeframe(milliseconds: int):
    result_dict = {'timeframe': milliseconds}
    res = requests.post(AAS_URI+f"api/timeframe", json=result_dict) 
    print(res.status_code)
    return res
    # TODO error management