import dash

import plotly.express as px
from dash import Input, Output, State, dcc, html
import dash_bootstrap_templates as dbt
import dash_bootstrap_components as dbc
from views.graph_duty_cycle import graph_duty_cycle
import plotly.graph_objects as go
from views.network_topology import topo_graph
from views.graph_icmp_packets import get_icmp_graph
from views.graph_pdr import get_pdr_graph
from views.graph_queue_loss import get_queueloss_graph
from views.graph_received_packets import get_receivedpackets_graph
import pandas as pd
from utils.data_connectors import get_network_data
from datetime import datetime
# from app import server

dash.register_page(__name__, path="/")

graph_duty_cycle = dcc.Graph(id="graph_duty_cycle")
graph_e2e_metric = dcc.Graph(id="graph-e2e", figure=px.bar(title="Average End to End Delay"))
graph_deadloss_metric = dcc.Graph(id="graph-deadloss", figure=px.bar(title="Deadline Loss Percentage"))

layout = html.Div(
    children=[
        dbc.Row(dbc.Col(
            html.Div(dbc.Spinner(html.Div(id="loading-output")), className='loader-spinner'),
            xs=12
        )),
        dbc.Row(
            [
                dbc.Col(get_receivedpackets_graph(is_init=True), md=6, style={"margin-top": "16px"}),
                dbc.Col(get_queueloss_graph(is_init=True), md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_e2e_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_deadloss_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(get_pdr_graph(is_init=True), md=6, style={"margin-top": "16px"}),
                dbc.Col(get_icmp_graph(is_init=True), md=6, style={"margin-top": "16px"}),

            ]),
        dbc.Row([
                    dbc.Col(topo_graph, md=8, style={"margin-top": "16px"}),
                    dbc.Col(graph_duty_cycle, md=4, style={"margin-top": "16px"}),
                ]) 
        
    ]
)

# Callback to update data in graphs (runs every 5 sec)
@dash.callback(Output("graph-receivedpackets", "figure"),
    Output("graph-queueloss", "figure"),
    Output("graph-e2e", "figure"),
    Output("graph-deadloss", "figure"),
    Output("graph_duty_cycle", "figure"),
    Output("graph-pdr", "figure"),
    Output("graph-icmp", "figure"),
    Output("loading-output", "children"),
[Input('url', 'pathname'), Input('refresh-dash', 'n_clicks')])
def data_scheduler(pathname, n_clicks):
    print(n_clicks)
    if pathname != '/':
        return dash.no_update

    api_data  = get_network_data()

    df_pdr = pd.DataFrame(api_data['pdr_metric'])
    if len(api_data['pdr_metric']) == 0:
        pdr_graph = get_pdr_graph(is_empty=True)
    else:      
        pdr_graph = get_pdr_graph(df_pdr)
    
    df_icmp = pd.DataFrame(api_data['icmp_metric'])
    if len(api_data['icmp_metric']) == 0:
        icmp_graph = get_icmp_graph(is_empty=True)
    else:
        icmp_graph = get_icmp_graph(df_icmp)
        
    #graph for queueloss
    df_queueloss = pd.DataFrame(api_data['queueloss_metric'])
    if len(api_data['queueloss_metric']) == 0:
        queueloss_graph = get_queueloss_graph(is_empty=True)
    else:
        queueloss_graph = get_queueloss_graph(df_queueloss)

    #graph for received packets
    df_received = pd.DataFrame(api_data['received_metric'])
    if len(api_data['received_metric']) == 0:
        received_graph = get_receivedpackets_graph(is_empty=True)
    else:
        received_graph = get_receivedpackets_graph(df_received)
    
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
    
    data_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return (received_graph, queueloss_graph, e2e_graph, deadloss_graph, graph_duty_cycle, pdr_graph, icmp_graph, f"Last Updated: {data_update}")