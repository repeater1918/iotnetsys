import dash

from dash import html, dcc
import plotly.express as px
from dash import Input, Output, State, dcc, html
import dash_bootstrap_templates as dbt
import dash_bootstrap_components as dbc
from views.graph_duty_cycle import graph_duty_cycle
import plotly.graph_objects as go

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
        dcc.Interval(
            id="interval-component",
            interval=5 * 1000,  # check for a data update every 5 seconds
        ),
        dbc.Row(
            [
                dbc.Col(graph_received_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_queue_loss, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_e2e_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_deadloss_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_pdr_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_pdr_metric, md=6, style={"margin-top": "16px"}),

            ]),
        dbc.Row([
                    dbc.Col(graph_icmp_metric, md=8, style={"margin-top": "16px"}),
                    dbc.Col(graph_duty_cycle, md=4, style={"margin-top": "16px"}),
                ]) 
        
    ]
)