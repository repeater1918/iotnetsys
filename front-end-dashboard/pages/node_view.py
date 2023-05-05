import dash
import plotly.express as px
from dash import Input, Output, State, dcc, html
import dash_bootstrap_templates as dbt
import dash_bootstrap_components as dbc
from views.graph_icmp_packets import get_icmp_graph
from views.graph_pdr import get_pdr_graph
from views.graph_queue_loss import get_queueloss_graph
from views.graph_hop_count import get_hop_cnt_graph

import pandas as pd


dash.register_page(__name__, path_template='/node_view/<nodeid>')


def layout(nodeid):
    
    graph_duty_cycle = dcc.Graph(id={"type": "graph-duty-cycle", "page": "node"} )
    graph_e2e_metric = dcc.Graph(id={"type": "graph-e2e", "page": "node"}, figure=px.bar(title="Average End to End Delay"))
    graph_deadloss_metric = dcc.Graph(id={"type": "graph-deadloss", "page": "node"}, figure=px.bar(title="Deadline Loss Percentage"))
    graph_pc_node_metric = dcc.Graph(id={"type": "graph-pc", "page": "node"}, figure = px.bar(title="Parent Changes per Node"))

    return html.Div(
    children=[
        dbc.Row(dbc.Col(
            html.Div(dbc.Spinner(html.Div(id={'type':"loading-output", 'page': "node"})), className='loader-spinner'),
            xs=12
            )),
        dbc.Row(
            [
                dbc.Col(get_pdr_graph(is_init=True, node_id=nodeid), md=6, style={"margin-top": "16px"}),
                dbc.Col(get_queueloss_graph(is_init=True, node_id=nodeid), md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_e2e_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_deadloss_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(get_hop_cnt_graph(is_init=True, node_id=nodeid), md=6, style={"margin-top": "16px"}),                
                dbc.Col(get_icmp_graph(is_init=True, node_id=nodeid), md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_pc_node_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_duty_cycle, md=6, style={"margin-top": "16px"}),
            ]),
       
        
    ]
)

#Callback
