import plotly.express as px
from dash import dcc, html
from pandas import DataFrame
import dash_bootstrap_templates as dbt

dbt.load_figure_template("DARKLY")

def get_receivedpackets_graph(data = None, is_init=False, node_id=False, is_empty=False):
    """Drawing parent change graph
    :param data: topology data
    :param is_init True if graph is first loaded
    :param node_id: nodeid to view
    :param is_empty: draw graph with no data
    """
    if is_init:
        # first initialization of the graph, just need empty placeholder and identify the object in html tree
        graph_id = {"type": "graph-receivedpackets", "page": "node" if node_id else "network"} 
        #graph_id = "graph-queueloss"
        title = f"Number of received packets - Node: {node_id}" if node_id else "Number of received packets"
        #title = "Queue Loss"
        receivedpackets_graph = _get_place_holder()

        return html.Div(
            children=[
                html.Div(title, className="graph-title"),
                dcc.Graph(id=graph_id, figure=receivedpackets_graph),
            ]
        )
    
    if is_empty:
        #  update has occurred but not data, return a empty placeholder
        return _get_place_holder()
    
    receivedpackets_graph = px.area(
            data,
            x="env_timestamp",
            y="total_packets",
            markers=True,
            labels={"env_timestamp": "Time Invervals", "total_packets": "Number of packets"},
        )
    
    receivedpackets_graph = _style_graph(receivedpackets_graph, data)
    return receivedpackets_graph

def _get_place_holder():
    fig = _style_graph(px.line())
    return fig

def _style_graph(fig, data: DataFrame = None):
    fig.update_layout({"plot_bgcolor": "#222", "paper_bgcolor": "#222"})
    return fig
