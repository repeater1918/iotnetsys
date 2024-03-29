from dash import html
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc

"""
Includes components for a network topology diagram: default_stylesheet, & cytoscape graph
"""
default_stylesheet = [
    {   'selector': 'node',
        'style': {
            'background-color': '#BFD7B5',
            'label': 'data(label)',
            'color': "white",
            'font-size': '1.5em',
            'width': "50%",
            'height': "50%",
        }
        
    },
    {
        'selector': 'edge',
        'style': {
            'curve-style': 'bezier',
            'target-arrow-color': 'white',
            'target-arrow-shape': 'triangle',
            'line-color': 'green'
        }
            }
]

topo_graph = html.Div([
    html.Div("Topology Diagram", className='graph-title'),
    cyto.Cytoscape(
        id='topology-graph',
        userPanningEnabled = False,
        responsive = True,
        layout={'name': 'breadthfirst','fit': True },
        elements=[],
        stylesheet=default_stylesheet,
        style={'width': '100%', 'left': '0px','height': '450px', 'z-index': -1},
        
    ),
    dbc.Toast(
        [html.P("", className="mb-0")],
        id="topo-toast",                       
        dismissable=True,
        is_open=False,
        style={"position": "relative", "top": -440, "width": 250, "z-index": 2}
    ),
    
])
