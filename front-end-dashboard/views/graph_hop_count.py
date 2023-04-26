import plotly.express as px
from dash import dcc, html
import plotly.graph_objects as go

def get_hop_cnt_graph(data = None, is_init=False, node_id=False, is_empty=False):

    if is_init:
        # first initialization of the graph, just need empty placeholder and identify the object in html tree
        graph_id = "graph-hopcount-node" if node_id else "graph-hopcount"
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
    max_hop_cnt = data['hop_count'].max()
    if node_id:
        #  data is available and a node type graph is required, render graph for a node view
        #breakpoint()
        
        hop_cnt_graph = go.Figure(
                        go.Indicator(
                            mode="gauge+number+delta",
                            value=data.loc[data['node'] == node_id, 'hop_count'].values[0],
                            domain={"x": [0, 1], "y": [0, 1]},
                            delta={"reference": avg_hop_cnt, "increasing": {"color": "#FF4136"},"decreasing": {"color": "green"}},
                            title={"text": "Hop Count"},
                            gauge={
                                "axis": {"range": [None, max_hop_cnt]},
                                "steps": [
                                    {"range": [0, 1], "color": "gray"},
                                ],
                            },
                        ),
                        layout={"plot_bgcolor": "#222", "paper_bgcolor": "#222"},
                    ),
        

        return hop_cnt_graph


    #  data is available and a node type graph is required, render graph for a node view
    hop_cnt_graph =  go.Figure(
                        go.Indicator(
                            mode="gauge+number+delta",
                            value=0,
                            domain={"x": [0, 1], "y": [0, 1]},
                            delta={"reference": avg_hop_cnt, "increasing": {"color": "#FF4136"},"decreasing": {"color": "#FF4136"}},
                            title={"text": "Hop Count Level"},
                            gauge={
                                "axis": {"range": [None, max_hop_cnt]},
                                "steps": [
                                    {"range": [0, 1], "color": "gray"},
                                ],
                            },
                        ),
                        layout={"plot_bgcolor": "#222", "paper_bgcolor": "#222"},
                    ),

    return hop_cnt_graph


def _get_place_holder():
    fig = go.Figure()
    return fig


