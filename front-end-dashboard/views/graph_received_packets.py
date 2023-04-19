import plotly.express as px
from dash import dcc, html
from pandas import DataFrame
import dash_bootstrap_templates as dbt

dbt.load_figure_template("DARKLY")

def get_receivedpackets_graph(data = None, is_init=False, node_id=False, is_empty=False):

    if is_init:
        # first initialization of the graph, just need empty placeholder and identify the object in html tree
        graph_id = "graph-receivedpackets-node" if node_id else "graph-receivedpackets"
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
    
    receivedpackets_graph = px.line(
            data,
            x="env_timestamp",
            y="total_packets",
            labels={"env_timestamp": "Time Invervals", "total_packets": "Number of packets"},
        )
    
    receivedpackets_graph = _style_graph(receivedpackets_graph, data)
    return receivedpackets_graph

def _get_place_holder():
    fig = _style_graph(px.bar())
    return fig

def _style_graph(fig, data: DataFrame = None):
    fig.update_layout({"plot_bgcolor": "#222", "paper_bgcolor": "#222"})
    if data is not None:
        fig.update_traces(line_color="blue")
    return fig
