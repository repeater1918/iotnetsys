import dash
from dash import html, dcc, Output, Input, ctx
import dash_bootstrap_components as dbc
import requests

dash.register_page(__name__, path='/hiddenpage')

def layout():   
    return html.Div(children=[
                dbc.Container([ 
                    dbc.Row(
                            [
                            html.H1("Welcome to CS44-2 IoT Dashboard", style={'text-align': 'center'},className="h1")
                            ], justify="center", align="center", className="h-50"
                            ),

                    dbc.Row(
                        [
                            dbc.Col(dbc.Button(id='real-time-mode',children = [html.H1("Latest session", style={'text-align': 'center'},className="h3")], size="lg", href='/network_view'), width=5, className='d-flex justify-content-center'),
                            dbc.Col(dbc.Button(id='static-mode',children = [html.H1("View Old Run", style={'text-align': 'center'},className="h3")], size="lg", href='/sessionlist'), width=5, className='d-flex justify-content-center'),
                            html.Div(id="dummy-output-main", style={"display": "none"})
                            
                        ], justify='center', align='center', className='h-30'
                    ),
                    ],style={"height": "90vh"}),]   


)

# @dash.callback(Output('dummy-output-main','children'),
#                [Input('real-time-mode', 'n_clicks'),
#                 Input('static-mode', 'n_clicks')])
# def dashboard_realtime_selected(btn1, btn2):
#     print("dashboard trigger ")
#     if btn1 == None and btn2 == None:
#         return dash.no_update
#     button_clicked = ctx.triggered_id
#     if button_clicked == 'real-time-mode':
#         #Post the mode to aas 
        
#         print('Real-time mode selected')   
#         result_dict = {"sessionid": ""}
#         AAS_URI = "http://127.0.0.1:8000/api/"
#         res = requests.post(AAS_URI+f"sessiondata", json=result_dict)  
#         return '/network_view'
#     else:
#         #Post the mode to AAS
#         print("session view selected")
#         return '/sessionlist'

