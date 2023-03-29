import dash
from dash import html

dash.register_page(__name__, path='/node_view')

layout = html.Div(children=[
    html.H1(children='This is node view'),
])

