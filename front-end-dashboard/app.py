"""
Front-End

Renders UI dashboard and updates figures intermittently using callbacks

TODO:

1. Figure out how to visualise and create required metrics in Dash
2. Figure out format of updates and frequency
3. Design and implement based on 1 + 2
"""
import dash
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt
import flask
import pandas as pd

server = flask.Flask(__name__)
app = dash.Dash(
    __name__,
    use_pages=True,
    server=server,
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP],
)

import json
from datetime import datetime


import plotly.express as px
from dash import Input, Output, State, dcc, html, ctx
from dash_bootstrap_components._components.Container import Container
from flask import request
from components.navigation import navbar, main_page_heading, nav_drawer

# declare global variables that will be updated by AAS
global df_pdr, df_icmp, df_pc_network
df_pdr = df_icmp = df_pc_network = None

dbt.load_figure_template("DARKLY")

app.layout = html.Div(
    children=[
        navbar,
        html.Div(
            className="wrapper",
            children=[
                nav_drawer,
                html.Div(
                    className="remaining-width",
                    children=[
                        main_page_heading,
                        dbc.Row(dbc.Col(html.Div(children=dash.page_container))),
                    ],
                ),
            ],
        ),
    ]
)


# Callback to update data in graphs (runs every 5 sec)
@app.callback(
    Output("graph-pdr", "figure"),
    Output("graph-icmp", "figure"),
    [Input("interval-component", "n_intervals")],
)
def data_scheduler(n_intervals):
    global df_pdr, df_icmp

    # If data hasn't been udpate for my graph return an empty graph
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

    return (pdr_graph, icmp_graph)


# The AAS will send data to this endpoint, it will trigger when something is received
@server.route("/data-update", methods=["POST"])
def req():
    # Some data was received
    # breakpoint()
    print(f"data received = {request.json['owner']}")

    # Step 1 - who does this data belong to
    owner = request.json["owner"]
    # Step 2 - get the data payload and convert to dataframe
    data = pd.DataFrame(request.json["data"])

    """  ##### Add your updates here #####  """
    # Step 3 - use owner tag to identify who the update belongs to -- add your own conditions here:
    if owner == "pdr_metric":
        # Get the x and y data that the figure refers to
        global df_pdr
        df_pdr = data

    if owner == "icmp_metric":
        # Get the x and y data that the figure refers to
        global df_icmp
        df_icmp = data

    if owner == "pc_network_metric":
        # Get the x and y data that the figure refers to
        global df_pc_network
        df_pc_network = data

    """  #####  """

    # return OK/sucess reponse to AAS
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


if __name__ == "__main__":
    app.run_server(debug=True)
