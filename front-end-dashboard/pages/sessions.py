import dash
from dash import html, dcc, Output, Input, dash_table, ctx, State, MATCH
import dash_bootstrap_components as dbc
from datetime import datetime
from utils.data_connectors import get_session_data, send_sessionid
import pandas as pd
import requests

dash.register_page(__name__, path='/sessionlist')


def layout():
    return html.Div(
        className="wrapper",

        children=[
            html.Div(className='remaining-width', children=[
            dbc.Container([
                html.H1("Session History Table", style={'text-align':'center'}),
                html.Div(children = [html.Div("Please select one of session below and select view", style={'text-align':'center'}), 
                                     html.Div(children=[html.Div(id='session_selected',),
                                               dbc.Button('View',id='session_id_btn', size='md', href='/')], 
                                               className='d-grid gap-2 d-md-flex justify-content-md-end m-2'),
                                     ]),
                dbc.Row([
                    dash_table.DataTable(
                        id='session-datatable',
                        columns=[],
                        data=[],
                        sort_action="native",
                        editable=False,
                        cell_selectable =False,
                        sort_mode="multi",
                        row_selectable="single",   
                        selected_rows = [],                 
                        page_action="native",
                        page_current= 0,
                        page_size= 10,
                        style_header={
                        'backgroundColor': 'rgb(30, 30, 30)',
                        'color': 'white',
                        'textAlign': 'center',
                        
                    },
                    style_data={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white',
                        'textAlign': 'center',
                    },
                    ),                
                    ], justify="center", align="center", className="h-50"
                    
                    ),
                    
                    ])])
            
            ]
        )


@dash.callback(
        [Output('session-datatable', 'columns'),
          Output('session-datatable', 'data'),],
        Input('url', 'pathname'),
)
def update_session_table(pathname):
    """Update session id table """
    col = []
    data = None
    if pathname == '/sessionlist':
        res = get_session_data()
        if len(res) > 0:
            df = pd.DataFrame(res) 
            df.rename(columns={'sessionid': 'Session ID'}, inplace=True)
            df['Session ID'] = pd.to_datetime(df['Session ID'])
            df['Date'] = df['Session ID'].dt.strftime('%d-%m-%Y')
            df = df[['Date', 'Session ID']]
            col = [{"name": i, "id": i, "type": "datetime" } for i in df.columns]
            data = df.to_dict('records')
        
    return col, data


@dash.callback(Output('session_selected', "children"),
               Output('usr_session_data', 'data'),
   
    Input('session-datatable', "derived_virtual_data"),
    Input('session-datatable', "derived_virtual_selected_rows"),
    State('usr_session_data', 'data'),
    )
def update_browser_session(rows, derived_virtual_selected_rows, data ):  
    """Update session id to browser storage"""
    val = None
    div_output = ''

    #User didn't submit the view    
    if derived_virtual_selected_rows is None or len(derived_virtual_selected_rows) == 0:
        derived_virtual_selected_rows = ''
        val = None
        
    else:
        val = rows[int(derived_virtual_selected_rows[0])]['Session ID']
        dt = datetime.fromisoformat(val)
        day = dt.date()
        hh_mm = dt.strftime("%H:%M") 
        div_output = f'You selected a session on {day} at {hh_mm}'
        data = data or {'sessionid': ''}
        data['sessionid'] = val
    print(f"Data {data} has been added to user browser ")
    return div_output, data


@dash.callback(Output('url', 'pathname'),
               Input('session_id_btn','n_clicks'),
               State('usr_session_data', 'data'))
def submit_btn(n_clicks, data):
    """Submit button send data and redirect url, do nothing if button not clicked yet"""
    if n_clicks == None:        
        return "/sessionlist"
    else:
        res = send_sessionid(data['sessionid'])
        print(f"Function submit_btn send {res} to AAS")
        
        return '/'
