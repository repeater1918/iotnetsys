
import plotly.express as px
import plotly.graph_objects as go
from views.graph_icmp_packets import get_icmp_graph
from views.graph_pdr import get_pdr_graph
from views.graph_queue_loss import get_queueloss_graph
from utils.data_connectors import get_node_data, get_network_data

import pandas as pd
import dash
from dash import Output, Input, MATCH



def get_common_graph(api_data, nodeid=None):    
    """Generate the graphs use in both network & node pages: pdr, icmp, queueloss, e2e, deadloss, duty-cycle"""

    df_pdr = pd.DataFrame(api_data['pdr_metric'])
    if len(api_data['pdr_metric']) == 0:
      pdr_graph = get_pdr_graph(is_empty=True, node_id=nodeid)
    else:  
        pdr_graph = get_pdr_graph(df_pdr, node_id=nodeid)

    df_icmp = pd.DataFrame(api_data['icmp_metric'])
    if len(api_data['icmp_metric']) == 0:
        icmp_graph = get_icmp_graph(is_empty=True, node_id=nodeid)
    else:
        icmp_graph = get_icmp_graph(df_icmp, node_id=nodeid)

    df_queueloss = pd.DataFrame(api_data['queueloss_metric'])
    if len(api_data['queueloss_metric']) == 0:
        queueloss_graph = get_queueloss_graph(is_empty=True, node_id=nodeid)
    else:
        queueloss_graph = get_queueloss_graph(df_queueloss, node_id=nodeid)    
  
    # Nwe - for end to end delay
    df_e2e = pd.DataFrame(api_data['e2e_metric'])
    if len(api_data['e2e_metric']) == 0:
        e2e_graph = px.line(title="Average End to End Delay")
    else:
        e2e_graph = px.line(
            df_e2e,
            x="env_timestamp",
            y="average_delay",
            color_discrete_sequence=["red"],
            title="Average End to End Delay",
            labels={"env_timestamp": "Time Invervals", "average_delay": "Milli-Seconds"},
        )
        #e2e_graph.update_traces(marker_color="green")
        e2e_graph.update_traces(line_color='blue')

    # Nwe - for deadloss
    df_deadloss = pd.DataFrame(api_data['deadloss_metric'])
    if len(api_data['deadloss_metric']) == 0:
        deadloss_graph = px.line(title="Deadline Loss Percentage")
    else:
        deadloss_graph = px.line(
            df_deadloss,
            x="env_timestamp",
            y="deadloss_percent",
            title="Deadline Loss Percentage",
            labels={"env_timestamp": "Time Invervals", "deadloss_percent": "Deadline Loss Packets %"},
            
        )
        #deadloss_graph.update_traces(marker_color="green")
        deadloss_graph.update_traces(line_color='blue')
   
    df_energy = pd.DataFrame(api_data['energy_cons_metric'])
    if len(api_data['energy_cons_metric']) == 0:
        graph_duty_cycle = px.bar(title="Energy Consumption")
    else:
        graph_duty_cycle = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=df_energy.loc[0,"energy_cons"],
                    
                    domain={"x": [0, 1], "y": [0, 1]},
                    delta={"reference": 100},
                    title={"text": "Energy Consumption"},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "steps": [
                            {"range": [0, 400], "color": "gray"},
                        ],
                    },
                ),

                layout={"plot_bgcolor": "#222", "paper_bgcolor": "#222"},
            )        
      
    return (queueloss_graph, e2e_graph, deadloss_graph, graph_duty_cycle, pdr_graph, icmp_graph,)

#Callbacks for above graph
# @dash.callback(
# Output({"type": "graph-queueloss", "page": MATCH}, "figure"),
# Output({"type": "graph-e2e", "page": "network"}, "figure"),
# Output({"type":"graph-deadloss", "page": MATCH}, "figure"),
# Output({"type":"graph-duty-cycle", "page": MATCH}, "figure"),
# Output({"type":"graph-pdr", "page": MATCH}, "figure"),
# Output({"type":"graph-icmp", "page": MATCH}, "figure"),
# [Input('url', 'pathname'), Input('refresh-dash', 'n_clicks')])
# def update_common_graphs(pathname, n_clicks):
#     print("update ...")
#     if pathname.split('/')[1] == 'node_view':
#         nodeid = int(pathname.split('/')[-1])
#         api_data  = get_node_data(nodeid)
#     elif pathname == '/':
#         nodeid = None
#         api_data  = get_network_data()
#     else:
#         return dash.no_update
    
#     queueloss_graph, e2e_graph, deadloss_graph, graph_duty_cycle, pdr_graph, icmp_graph = get_common_graph(api_data, nodeid)

#     return (queueloss_graph, e2e_graph, deadloss_graph, graph_duty_cycle, pdr_graph, icmp_graph)

