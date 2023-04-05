from dash import Dash, html, Input, Output, State
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
import dash

#Static topology. Fix me: handle message from AAS api
#The dict returned from AAS in the below format
topology_data = [{'node': 2, 'sub_type_value': 1}, 
                {'node': 3, 'sub_type_value': 1}, 
                {'node': 5, 'sub_type_value': 2}, 
                {'node': 4, 'sub_type_value': 2}, 
                {'node': 6, 'sub_type_value': 3}, 
                {'node': 1, 'sub_type_value': 1}]

data_tuple = [tuple(id.values()) for id in topology_data] #Convert to tuple for cytoscape drawing

#Drawing node 
nodes = [
    {'data': {'id': str(node), 'label': str(node)}}
      for node,_ in data_tuple    
    ]

#Drawing links between source and its parent
edges = [
    {'data': {'source': str(source), 'target': str(target)}}
      for source, target in [tup for tup in data_tuple if tup[0] != tup[1]] #Don't draw link for root node
    ]

default_stylesheet = [
    {   'selector': 'node',
        'style': {
            'background-color': '#BFD7B5',
            'label': 'data(label)',
            'color': "white"
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
          layout={
              'name': 'breadthfirst',
              'roots': '[id = "1"]',
              
          },
          elements=edges+nodes,
          stylesheet=default_stylesheet,
          style={'width': '100%', 'left': '25px','height': '450px', 'z-index': -1}
      ),
      dbc.Toast(
            [html.P("", className="mb-0")],
            id="topo-toast",                       
            dismissable=True,
            is_open=False,
            style={"position": "relative", "top": -440, "width": 250, "z-index": 2}
        ),
     
    ])

@dash.callback(Output('topology-graph', 'stylesheet'),
                    Output('topo-toast', "is_open"),
                    Output('topo-toast', "header"),
                    Output("topo-toast", "children"),               
                    Input('topology-graph', 'selectedNodeData'),
                    [State('topo-toast', "is_open")])
def displayTapNodeData(data, is_open):
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
            toast_child = [html.P("My information is ....", className="mb-0"),]
            is_open = True

            if selected_node != '1':
                toast_child.append(dbc.Button("Go to node view", size="sm mt-2", href=f"/node_view/{selected_node}"))

            
        else: 
            #Dis-select node
            toast_child = []
            is_open = False
            toast_hdr = ''
            new_styles = []

        return default_stylesheet + new_styles, is_open, toast_hdr, toast_child