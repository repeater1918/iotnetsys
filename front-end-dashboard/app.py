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
import pandas as pd

print(f"Running in mode -> {os.environ.get('DEPLOYMENT', 'dev')}")

server = flask.Flask(__name__)
app = dash.Dash(
    __name__,
    use_pages=True,
    server=server,
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

UPDATE_INTERVAL = 5 * 1000 * 1000# check for a data update every 5 seconds

import json
from datetime import datetime

from dash import Input, Output, State, dcc, html, ctx
from dash_bootstrap_components._components.Container import Container
from flask import request
from components.navigation import navbar, nav_drawer, top_page_heading

# declare global variables that will be updated by AAS
global df_pdr, df_icmp
df_pdr = df_icmp = None

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
        html.P(id="testing")
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
@app.callback(Output('session_data', 'data'),
              Input('url', 'pathname'))
def update_session_storage(pathname):
    session_data = {'update-interval': UPDATE_INTERVAL}




if __name__ == "__main__":
    app.run(debug=True)