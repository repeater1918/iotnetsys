import plotly.express as px
from dash import dcc, html

def get_icmp_graph(data = None, is_init=False, node_id=False, is_empty=False):
    """Drawing icmp graph
    :param data: topology data
    :param is_init True if graph is first loaded
    :param node_id: nodeid to view
    :param is_empty: draw graph with no data
    """
    if is_init:
        # first initialization of the graph, just need empty placeholder and identify the object in html tree
        graph_id = {"type": "graph-icmp", "page": "node" if node_id else "network"} 
        title = f"ICMP Packets - Node: {node_id}" if node_id else "ICMP Packets"
        icmp_graph = _get_place_holder()

        return html.Div(
            children=[
                html.Div(title, className="graph-title"),
                dcc.Graph(id=graph_id, figure=icmp_graph),
            ]
        )
    
    if is_empty:
        #  update has occurred but not data, return a empty placeholder
        return _get_place_holder()
    
    if node_id:
        #  data is available and a node type graph is required, render graph for a node view
        icmp_graph = px.bar(
            data,
            x="env_timestamp",
            y="sub_type_value",
            labels={"env_timestamp": "Time", "sub_type_value": "Number of ICMP Packets"},
            )
        
        icmp_graph = _style_graph(icmp_graph)

        return icmp_graph


    #  data is available and a node type graph is required, render graph for a node view
    icmp_graph = px.bar(
        data,
        x="node",
        y="sub_type_value",
        labels={"node": "Node ID", "sub_type_value": "Number of ICMP Packets"},
    )
    icmp_graph = _style_graph(icmp_graph)

    return icmp_graph


def _get_place_holder():
    fig = _style_graph(px.bar())
    return fig

def _style_graph(fig):
    fig.update_traces(marker_color="#F48308")
    #fig.update_traces(marker_color="#1763F4")
    fig.update_xaxes(type="category")
    fig.update_layout({"plot_bgcolor": "#222", "paper_bgcolor": "#222"})
    return fig
