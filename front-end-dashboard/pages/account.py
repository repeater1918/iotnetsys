import dash
from dash import html, dcc

dash.register_page(__name__, path='/account')


layout = html.Div(children=[
    html.H1(children='This is our account page'),

])