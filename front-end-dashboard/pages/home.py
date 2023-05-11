import dash

import plotly.express as px
from dash import  dcc, html

import dash_bootstrap_components as dbc
from views.graph_duty_cycle import graph_duty_cycle
from views.network_topology import topo_graph
from views.graph_icmp_packets import get_icmp_graph
from views.graph_pdr import get_pdr_graph
from views.graph_queue_loss import get_queueloss_graph
from views.graph_received_packets import get_receivedpackets_graph
from components.navigation import nav_drawer, top_page_heading


dash.register_page(__name__, path="/")

graph_duty_cycle = dcc.Graph(id={"type": "graph-duty-cycle", "page": "network"})
graph_e2e_metric = dcc.Graph(id={"type": "graph-e2e", "page": "network"}, figure=px.bar(title="Average End to End Delay"))
graph_deadloss_metric = dcc.Graph(id={"type": "graph-deadloss", "page": "network"}, figure=px.bar(title="Deadline Loss Percentage"))

layout = html.Div(
    className="wrapper",
    children= [nav_drawer,
        
        html.Div(className='remaining-width', children=[
        *top_page_heading("Network level"),
        dbc.Row(dbc.Col(
            html.Div(dbc.Spinner(children = [html.Div(id={'type':"loading-output", 'page': "network"}),
                                             html.Div(id={'type':"experiment-id-div", 'page': "network"})]), className='loader-spinner'),
            xs=12
        )),
        dbc.Row(
            [
                dbc.Col(get_pdr_graph(is_init=True), md=6, style={"margin-top": "16px"}),
                dbc.Col(get_receivedpackets_graph(is_init=True), md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_e2e_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_deadloss_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(get_icmp_graph(is_init=True), md=6, style={"margin-top": "16px"}),
                dbc.Col(get_queueloss_graph(is_init=True), md=6, style={"margin-top": "16px"}),
                

            ]),
        dbc.Row([
                    dbc.Col(topo_graph, md=8, style={"margin-top": "16px"}),
                    dbc.Col(graph_duty_cycle, md=4, style={"margin-top": "16px"}),
                ]) 
    ])]      
   
)
