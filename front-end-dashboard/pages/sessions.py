import dash
from dash import html, dcc, Output, Input, dash_table
import dash_bootstrap_components as dbc
from datetime import datetime
from utils.data_connectors import get_session_data
import pandas as pd

#dash.register_page(__name__, path='/sessionlist') hide in development branch


def layout():
    return html.Div(
        children=[
            dbc.Container([
                html.H1("Session History Table", style={'text-align':'center'}),
                html.Div(children = [html.Div("Please select one of session below and select view", style={'text-align':'center'}), 
                                     html.Div([html.Div(id='session_view_value',),dbc.Button('View', size='md'), ], className='d-grid gap-2 d-md-flex justify-content-md-end m-2'),
                                     ]),
                dbc.Row([
                    dash_table.DataTable(
                        id='datatable-interactivity',
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
                
                html.Div(id='datatable-interactivity-container')
               
                
                    ])
            
            ]
        )


@dash.callback(
        [Output('datatable-interactivity', 'columns'),
          Output('datatable-interactivity', 'data'),],
        Input('url', 'pathname'),
)
def update_session_table(pathname):
    if pathname == '/sessionlist':
        res = get_session_data()
        if len(res) > 0:
            df1 = pd.DataFrame(res)            
            col = [{"name": i, "id": i, } for i in df1.columns]
            data = df1.to_dict('records')
        else:
            col = []
            data = None

    return col, data


@dash.callback(Output('session_view_value', "children"),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows")
    )
def update_graphs(rows, derived_virtual_selected_rows):
    if derived_virtual_selected_rows is None or len(derived_virtual_selected_rows) == 0:
        derived_virtual_selected_rows = ''
        output = ''
    else:
        val = rows[int(derived_virtual_selected_rows[0])]['Session Time']
        dt = datetime.fromisoformat(val)
        day = dt.date()
        hh_mm = dt.strftime("%H:%M") 
        output = f'You selected a session on {day} at {hh_mm}'
    return output