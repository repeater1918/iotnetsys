import dash
import plotly.express as px
from dash import Input, Output, State, dcc, html
import dash_bootstrap_templates as dbt
import dash_bootstrap_components as dbc
from views.graph_duty_cycle import graph_duty_cycle
from views.network_topology import topo_graph
from views.graph_icmp_packets import get_icmp_graph
from views.graph_pdr import get_pdr_graph
from views.graph_queue_loss import get_queueloss_graph
from views.graph_received_packets import get_receivedpackets_graph
from views.graph_hop_count import get_hop_cnt_graph
from utils.data_connectors import get_node_data, get_topo_data
import plotly.graph_objects as go
import pandas as pd

dash.register_page(__name__, path_template='/node_view/<nodeid>')


def layout(nodeid):
    
    graph_duty_cycle = dcc.Graph(id=f"graph_duty_cycle-node")
    graph_e2e_metric = dcc.Graph(id=f"graph-e2e-node", figure=px.bar(title="Average End to End Delay"))
    graph_deadloss_metric = dcc.Graph(id=f"graph-deadloss-node", figure=px.bar(title="Deadline Loss Percentage"))
    graph_pc_node_metric = dcc.Graph(id=f"graph-pc-node", figure = px.bar(title="Parent Changes per Node"))

    return html.Div(
    children=[
        dbc.Row(
            [
                dbc.Col(get_hop_cnt_graph(is_init=True, node_id=nodeid), md=6, style={"margin-top": "16px"}),
                dbc.Col(get_queueloss_graph(is_init=True, node_id=nodeid), md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_e2e_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_deadloss_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(get_pdr_graph(is_init=True, node_id=nodeid), md=6, style={"margin-top": "16px"}),
                dbc.Col(get_icmp_graph(is_init=True, node_id=nodeid), md=6, style={"margin-top": "16px"}),
            ]),
        dbc.Row([
                dbc.Col(graph_pc_node_metric, md=8, style={"margin-top": "16px"}),
                dbc.Col(graph_duty_cycle, md=4, style={"margin-top": "16px"}),
                ]) 
        
    ]
)

#Callback

@dash.callback(Output(f"graph-hopcount-node", "figure"),
Output(f"graph-queueloss-node", "figure"),
Output(f"graph-e2e-node", "figure"),
Output(f"graph-deadloss-node", "figure"),
Output(f"graph_duty_cycle-node", "figure"),
Output(f"graph-pdr-node", "figure"),
Output(f"graph-icmp-node", "figure"),
Output(f"graph-pc-node", "figure"),
[Input("interval-component", "n_intervals"),
    Input('url', 'pathname')])
def update_graph(n, pathname):
    nodeid = int(pathname.split('/')[-1])
    api_data  = get_node_data(nodeid)
    # If data hasn't been udpate for my graph return an empty graph
    #Using result from API directly
    
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
    
    topo_api_data = get_topo_data()
    df_topo = pd.DataFrame(topo_api_data)
    if len(topo_api_data) == 0:
        hopcount_graph = get_hop_cnt_graph(is_empty=True, node_id=nodeid)[0]
    else:
        hopcount_graph = get_hop_cnt_graph(df_topo, node_id = nodeid)[0]

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

    # df_queueloss = pd.DataFrame(api_data['queueloss_metric'])
    # if len(api_data['queueloss_metric']) == 0:
    #     queueloss_graph = px.bar(title="Queue loss")
    # else:
    #     queueloss_graph = px.bar(
    #         df_queueloss,
    #         x="node",
    #         y="sub_type_value",
    #         title="Queue loss",
    #         labels={"node": "Node ID", "sub_type_value": "Number of dropped packets"},
    #     )
    # queueloss_graph.update_traces(marker_color='blue')
    # queueloss_graph.update_xaxes(type='category')
        
    df_energy = pd.DataFrame(api_data['energy_cons_metric'])
    if len(api_data['energy_cons_metric']) == 0:
        graph_duty_cycle = px.bar(title="Average energy consumption")
    else:
        graph_duty_cycle = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=df_energy.loc[0,"energy_cons"],
                    
                    domain={"x": [0, 1], "y": [0, 1]},
                    delta={"reference": 100},
                    title={"text": "Average energy consumption"},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "steps": [
                            {"range": [0, 400], "color": "gray"},
                        ],
                    },
                ),

                layout={"plot_bgcolor": "#222", "paper_bgcolor": "#222"},
            )

    df_pc_node = pd.DataFrame(api_data['pc_metric_node'])
    if len(api_data['pc_metric_node']) == 0:
        pc_node_graph = px.bar(title="Parent Changes per Node")
    else:
        pc_node_graph = px.bar(

            df_pc_node,
            x="node",
            y="parent_changes",
            title="Parent Changes per Node",
            labels={"node": "Node ID", "parent_changes": "Total Parent Changes"},
        )
        pc_node_graph.update_traces(marker_color="blue")

    return (hopcount_graph, queueloss_graph, e2e_graph,deadloss_graph,graph_duty_cycle, pdr_graph, icmp_graph, pc_node_graph)
