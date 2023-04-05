import dash

import plotly.express as px
from dash import Input, Output, State, dcc, html
import dash_bootstrap_templates as dbt
import dash_bootstrap_components as dbc
from views.graph_duty_cycle import graph_duty_cycle
import plotly.graph_objects as go
from views.network_topology import topo_graph
import pandas as pd
from utils.data_connectors import get_network_data

# from app import server

dbt.load_figure_template("DARKLY")

dash.register_page(__name__, path="/")

graph_pdr_metric = dcc.Graph(id="graph-pdr", figure=px.bar(title="Percentage Packet Loss"))
graph_icmp_metric = dcc.Graph(id="graph-icmp", figure=px.bar(title="ICMP Packets"))
graph_received_metric = dcc.Graph(id="graph-received", figure=px.line(title="Number of received packets"))
graph_queue_loss = dcc.Graph(id="graph-queueloss", figure=px.bar(title="Queue loss"))
graph_duty_cycle = dcc.Graph(id="graph_duty_cycle")
graph_e2e_metric = dcc.Graph(id="graph-e2e", figure=px.bar(title="Average End to End Delay"))
graph_deadloss_metric = dcc.Graph(id="graph-deadloss", figure=px.bar(title="Deadline Loss Percentage"))

layout = html.Div(
    children=[
        dbc.Row(
            [
                dbc.Col(graph_received_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_queue_loss, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_e2e_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_deadloss_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_pdr_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_icmp_metric, md=6, style={"margin-top": "16px"}),

            ]),
        dbc.Row([
                    dbc.Col(topo_graph, md=8, style={"margin-top": "16px"}),
                    dbc.Col(graph_duty_cycle, md=4, style={"margin-top": "16px"}),
                ]) 
        
    ]
)

# Callback to update data in graphs (runs every 5 sec)
@dash.callback(Output("graph-received", "figure"),
    Output("graph-queueloss", "figure"),
    Output("graph-e2e", "figure"),
    Output("graph-deadloss", "figure"),
    Output("graph_duty_cycle", "figure"),
    Output("graph-pdr", "figure"),
    Output("graph-icmp", "figure"),
    [Input("interval-component", "n_intervals"),
      Input('url', 'pathname')],)
def data_scheduler(n_intervals, pathname):
    api_data  = get_network_data()
    if pathname == '/':
        # If data hasn't been udpate for my graph return an empty graph
        #Using result from API directly        
        df_pdr = pd.DataFrame(api_data['pdr_metric'])
        if type(df_pdr) == type(None):
            pdr_graph = px.line(title="Percentage Packet Loss")
        else:      
            pdr_graph = px.line(
                df_pdr,
                x="env_timestamp",
                y=["failed_packets_precentage", "successful_packets_precentage"],
                color_discrete_sequence=["red", "blue"],
                title="Packet Delivery Ratios",
                labels={"env_timestamp": "Time Invervals", "value": "Percentage"},
            )

    df_icmp = pd.DataFrame(api_data['icmp_metric'])
    if type(df_icmp) == type(None):
        icmp_graph = px.bar(title="ICMP Packets")
    else:
        icmp_graph = px.bar(
            df_icmp,
            x="node",
            y="sub_type_value",
            title="ICMP Packets",
            labels={"node": "Node ID", "sub_type_value": "Total ICMP Packets"},
        )
        icmp_graph.update_traces(marker_color="green")
    #nomin

    df_received = pd.DataFrame(api_data['received_metric'])
    if type(df_received) == type(None):
        received_graph = px.line(title="Number of received packets")
    else:
        received_graph = px.line(
            df_received,
            x="env_timestamp",
            y="total_packets",
            title="Number of received packets",
            labels={"env_timestamp": "Time Invervals", "total_packets": "Number of packets"},
        )
        # Nwe - for end to end delay
    df_e2e = pd.DataFrame(api_data['e2e_metric'])
    if type(df_e2e) == type(None):
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
    if type(df_deadloss) == type(None):
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

    df_queueloss = pd.DataFrame(api_data['queueloss_metric'])
    if type(df_queueloss) == type(None):
        queueloss_graph = px.bar(title="Queue loss")
    else:
        queueloss_graph = px.bar(
            df_queueloss,
            x="node",
            y="sub_type_value",
            title="Queue loss",
            labels={"node": "Node ID", "sub_type_value": "Number of dropped packets"},
        )
    #nomin  
    df_energy = pd.DataFrame(api_data['energy_cons_metric'])
    if type(df_energy) == type(None):
        graph_duty_cycle = px.bar(title="Energy Level")
    else:
        graph_duty_cycle = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=df_energy.loc[0,"energy_cons"],
                    
                    domain={"x": [0, 1], "y": [0, 1]},
                    delta={"reference": 100},
                    title={"text": "Energy Level"},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "steps": [
                            {"range": [0, 400], "color": "gray"},
                        ],
                    },
                ),

                layout={"plot_bgcolor": "#222", "paper_bgcolor": "#222"},
            )

    return (received_graph, queueloss_graph, e2e_graph,deadloss_graph,graph_duty_cycle, pdr_graph, icmp_graph)