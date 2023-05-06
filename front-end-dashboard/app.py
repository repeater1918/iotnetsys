"""
Front-End
Renders UI dashboard and updates figures intermittently using callbacks
TODO:
1. Figure out how to visualise and create required metrics in Dash
2. Figure out format of updates and frequency
3. Design and implement based on 1 + 2
"""
import os
import dash
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt
import flask
from utils.data_connectors import send_timeframe, send_dlloss, get_network_data, get_node_data
from utils.graph_utils import get_common_graph
from dash import MATCH
from maindash import app 
print(f"Running in mode -> {os.environ.get('DEPLOYMENT', 'dev')}")

UPDATE_INTERVAL = 5 * 1000 # check for a data update every 5 seconds

import json
from datetime import datetime

from dash import Input, Output, State, dcc, html, ctx
from dash_bootstrap_components._components.Container import Container
from flask import request
from components.navigation import navbar, nav_drawer, top_page_heading

dbt.load_figure_template("darkly")


app.layout = html.Div(
    children=[
        navbar,
        dcc.Location(id='url', refresh=False),
        # dcc.Store stores the session var
        dcc.Store(id='session_data'),
        dcc.Interval(
            id="interval-component",
            interval= UPDATE_INTERVAL,  
        ),
        html.Div(id='usr-tz', style={"display":"none"}),
        html.Div(
            className="wrapper",
            
            children=[
                nav_drawer,
                html.Div(
                    className="remaining-width",
                    id="page_heading",
                    children=[
                        *top_page_heading("Network Level")                       
                        
                    ],
                ),
            ],
        ),
    ]
)

#child_container = dbc.Row(dbc.Col(html.Div(children=dash.page_container)))

@app.callback(
        Output("page_heading", 'children'),
        Input('url', 'pathname'),
        
)
def load_heading(pathname):
    if 'node_view' in pathname:
        node_heading_str = f"Node {pathname.split('/')[-1]}"
        return top_page_heading(node_heading_str)
    else: 
        return top_page_heading("Network Level")


#App management callbacks
@app.callback(
    Output("dropdown-timeframe", "required"),
    Input("dropdown-timeframe", "value")
)
def set_timeframe(value):
    if value == None:
        send_timeframe(60000) #default 1 min
    else:
        send_timeframe(value)

#App management callbacks
@app.callback(
    Output("dropdown-dlloss", "required"),
    Input("dropdown-dlloss", "value")
)
def set_timeframe(value):
    print(f"Timeframe set {value}")
    if value == None:
        send_dlloss(25) #default 25ms
    else:
        send_dlloss(value)

#Client callback to get tz
app.clientside_callback(
     """
    function(id) {          
        const offset = new Date().getTimezoneOffset();                 
        return offset
    }
    """,
    Output('usr-tz', 'children'),
    Input('usr-tz', 'id'),
)


if __name__ == "__main__":
    app.run(debug=True)
