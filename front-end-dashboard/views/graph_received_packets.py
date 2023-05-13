import plotly.express as px
from dash import dcc, html
from pandas import DataFrame
import dash_bootstrap_templates as dbt

def get_receivedpackets_graph(data = None, is_init=False, is_empty=False):
    """Drawing number of received packet graph
    :param data: topology data
    :param is_init True if graph is first loaded
    :param is_empty: draw graph with no data
    """
    if is_init:
        # first initialization of the graph, just need empty placeholder and identify the object in html tree
        graph_id = {"type": "graph-receivedpackets", "page": "network"} 
        title = "Number of received packets"
        receivedpackets_graph = _get_place_holder()

        return html.Div(
            children=[
                html.Div(title, className="graph-title"),
                dcc.Graph(id=graph_id, figure=receivedpackets_graph),
            ])
    
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
    fig.update_traces(line_color = '#1BF646')
    return fig
