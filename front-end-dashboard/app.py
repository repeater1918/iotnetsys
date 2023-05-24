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
from utils.data_connectors import send_timeframe, send_dlloss
from utils.graph_utils import get_common_graph
from dash import MATCH
from maindash import app, server 
print(f"Running in mode -> {os.environ.get('DEPLOYMENT', 'dev')}")

UPDATE_INTERVAL = 5 * 1000 # check for a data update every 5 seconds


from dash import Input, Output, State, dcc, html, ctx
from dash_bootstrap_components._components.Container import Container
from flask import request
from components.navigation import navbar

dbt.load_figure_template("darkly")


app.layout = html.Div(
    children=[
        navbar,
        dcc.Location(id='url', refresh=False),
        # dcc.Store stores the session var
        dcc.Store(id='usr_session_data', storage_type='session'),
        dcc.Interval(
            id="interval-component",
            interval= UPDATE_INTERVAL,  
        ),
        html.Div(id='usr-tz', style={"display":"none"}),
        html.Div(            
            id="wrapper-drawer",
            children=[
                dbc.Row(dbc.Col(html.Div(children=dash.page_container)))
            ],
            style={"padding-right": "16px", },
        ),
    ]
)

#App management callbacks
@app.callback(
    Output("dropdown-timeframe", "required"),
    [Input("dropdown-timeframe", "value"),
    Input('refresh-dash', 'n_clicks')]
)
def set_timeframe(value, btn_refresh):
    """Callback to send timeframe selected to AAS"""
    #print(f"Timeframe set {value}")
    if value == None:
        send_timeframe(60000) #default 1 min
    else:
        send_timeframe(value)

#App management callbacks
@app.callback(
    Output("dropdown-dlloss", "required"),
    [Input("dropdown-dlloss", "value"),
    Input('refresh-dash', 'n_clicks')]
)
def set_dlloss(value, btn_refresh):
    """Callback to send deadline_loss selected to AAS"""
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
