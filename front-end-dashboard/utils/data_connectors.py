import requests

AAS_URI = "http://127.0.0.1:8000/" #AAS supports networklv_data or nodelv_data
global supported_metrics
supported_metrics = ["pdr_metric","icmp_metric","received_metric", "e2e_metric", "deadloss_metric", "queueloss_metric","energy_cons_metric"]

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
    for v in supported_metrics:
        res = requests.get(AAS_URI+f"node_data/{v}?node={nodeid}") 
        if res.status_code == 200:
            res = res.json()
        else:
            res = []
        result_dict[v] = res
    #print ("Cache updated at ", datetime.now())
    return result_dict
