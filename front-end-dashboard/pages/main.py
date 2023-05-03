import dash
from dash import html, dcc
import dash_bootstrap_components as dbc


#dash.register_page(__name__, path='/') Hide in official branch 

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
                            dbc.Col(dbc.Button(html.H1("Real-Time Mode", style={'text-align': 'center'},className="h3"), size="lg", href='/network_view'), width=5, className='d-flex justify-content-center'),
                            dbc.Col(dbc.Button(html.H1("View Old Run", style={'text-align': 'center'},className="h3"), size="lg", href='/sessionlist'), width=5, className='d-flex justify-content-center'),
                            
                            
                        ], justify='center', align='center', className='h-30'
                    ),
                    ],style={"height": "90vh"}),]    

)