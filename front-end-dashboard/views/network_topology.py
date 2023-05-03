from dash import Dash, html, Input, Output, State
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
import dash
from utils.data_connectors import get_topo_data


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
        layout={'name': 'breadthfirst'},
        elements=[],
        stylesheet=default_stylesheet,
        style={'width': '100%', 'left': '25px','height': '450px', 'z-index': -1},
        
    ),
    dbc.Toast(
        [html.P("", className="mb-0")],
        id="topo-toast",                       
        dismissable=True,
        is_open=False,
        style={"position": "relative", "top": -440, "width": 250, "z-index": 2}
    ),
    
])
global roots
roots = set()
@dash.callback(
         Output("topology-graph", 'elements'),
         Output('topology-graph','layout'),
        [Input('topology-graph', 'elements'),
         Input('topology-graph', 'layout'),
         Input('url', 'pathname'), Input('refresh-dash', 'n_clicks')]
        
)
def topology_update(elements, layout, pathname, n_clicks):
    """Callback to extract topology and draw"""
    ele = []
    
    topology_data = get_topo_data()
    global roots
    for v in topology_data:     
        if v['role'] == 'server':
            roots.add(f"{v['node']}")

        ele.append({'node': v['node'], 'parent': v['parent']})

    data_tuple = [tuple(id.values()) for id in ele] #Convert to tuple for cytoscape drawing
    # Drawing nodes 
    nodes = [{'data': {'id': str(node), 'label': str(node)}} for node,_ in data_tuple ]
    #Drawing links between source and its parent
    edges = [
        {'data': {'source': str(source), 'target': str(target)}}
        for source, target in [tup for tup in data_tuple if str(tup[0]) not in roots] #Don't draw link for root node
        ]
    layout['roots'] = '#'+',#'.join(roots)   
     
    return edges+nodes, layout



@dash.callback(Output('topology-graph', 'stylesheet'),
                    Output('topo-toast', "is_open"),
                    Output('topo-toast', "header"),
                    Output("topo-toast", "children"),               
                    Input('topology-graph', 'selectedNodeData'),
                    [State('topo-toast', "is_open")])
def displayTapNodeData(data, is_open):
        global roots
        if data:
            #Node data[0]['id'] selected
            selected_node = data[0]['id']
            new_styles = [
            {
                'selector': 'node[id = "{}"]'.format(selected_node),
                'style': {
                    'background-color': "green",                 
                }
            }]
            toast_hdr = [html.P(f"Node {selected_node}", className="mb-0", style={"color": "white"})]            
            is_open = True
            
            if str(selected_node) not in roots:
                toast_child = [html.P("I'm a sensor ", className="mb-0"),]
                toast_child.append(dbc.Button("Go to node view", size="sm mt-2", href=f"/node_view/{selected_node}"))
            else:
                 toast_child = [html.P("I'm a server", className="mb-0"),]

            
        else: 
            #Dis-select node
            toast_child = []
            is_open = False
            toast_hdr = ''
            new_styles = []

        return default_stylesheet + new_styles, is_open, toast_hdr, toast_child
