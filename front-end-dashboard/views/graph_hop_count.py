import plotly.express as px
from dash import dcc, html
import plotly.graph_objects as go

def get_hop_cnt_graph(data = None, is_init=False, node_id=False, is_empty=False):
    """Drawing hop count graph
    :param data: topology data
    :param is_init True if graph is first loaded
    :param node_id: nodeid to view
    :param is_empty: draw graph with no data
    """
    if is_init:
        # first initialization of the graph, just need empty placeholder and identify the object in html tree
        graph_id = {"type": "graph-hopcount", "page": "node" if node_id else "network"} 
        title = f"Hop count value - Node: {node_id}" if node_id else "Avg Network Hop Count"
        hop_cnt_graph = _get_place_holder()

        return html.Div(
            children=[
                html.Div(title, className="graph-title"),
                dcc.Graph(id=graph_id, figure=hop_cnt_graph),
            ]
        )
    
    if is_empty:
        #  update has occurred but not data, return a empty placeholder
        return _get_place_holder()
    
    server_node = data.loc[data['role'] == 'server', 'node'].values[0]
    avg_hop_cnt = round(data.loc[data['node'] != server_node, 'hop_count'].mean(),2)

    if node_id:
        #  data is available and a node type graph is required, render graph for a node view       
        hop_cnt_graph = go.Figure(
                        go.Indicator(
                            mode="number",
                            value=data.loc[data['node'] == node_id, 'hop_count'].values[0],
                            number={"font":{"size":100}},
                            domain={"row":0, "column": 1},                          
                            title = {"text": f"<span style='font-size:0.9em;color:gray'> Average is {avg_hop_cnt} </span><br>"}
                            
                        ),                       
                        layout={"plot_bgcolor": "#222", "paper_bgcolor": "#222",},
                    ),
        

        return hop_cnt_graph


    #  data is available and a node type graph is required, render graph for a node view
    hop_cnt_graph =  go.Figure(
                        go.Indicator(
                            mode="number",
                            value=0,
                            domain={"x": [0, 1], "y": [0, 1]},
                            title={"text": "Hop Count Level"},
                           
                        ),
                        layout={"plot_bgcolor": "#222", "paper_bgcolor": "#222"},
                    ),

    return hop_cnt_graph


def _get_place_holder():
    fig = go.Figure()
    return fig



