import plotly.express as px
from dash import dcc, html
import plotly.graph_objects as go
from pandas import DataFrame


def get_deadloss_graph(data = None, is_init=False, node_id=False, is_empty=False):
    """Drawing deadline loss graph
    :param data: topology data
    :param is_init True if graph is first loaded
    :param node_id: nodeid to view
    :param is_empty: draw graph with no data
    """
    if is_init:
        # first initialization of the graph, just need empty placeholder and identify the object in html tree
        graph_id = {"type": "graph-deadloss", "page": "node" if node_id else "network"} 
        title = f"Deadline Loss Percentage - Node: {node_id}" if node_id else "Deadline Loss Percentage"
        deadloss_graph = _get_place_holder()

        return html.Div(
            children=[
                html.Div(title, className="graph-title"),
                dcc.Graph(id=graph_id, figure=deadloss_graph),
            ]
        )
    
    if is_empty:
        #  update has occurred but not data, return a empty placeholder
        return _get_place_holder()
    
    if node_id:
        #  data is available and a node type graph is required, render graph for a node view
        deadloss_graph = px.area(
            data,
            x="env_timestamp",
            y="deadloss_percent",
            labels={"env_timestamp": "Time Invervals", "deadloss_percent": "Deadline Loss Packets (%)"},
        )
        deadloss_graph = _style_graph(deadloss_graph, data)

        return deadloss_graph


    #  data is available and a node type graph is required, render graph for a node view
    deadloss_graph = px.area(
            data,
            x="env_timestamp",
            y="deadloss_percent",
            labels={"env_timestamp": "Time Invervals", "deadloss_percent": "Deadline Loss Packets (%)"},
        )
    deadloss_graph = _style_graph(deadloss_graph, data)

    return deadloss_graph


def _get_place_holder():
    fig = _style_graph(px.line())
    return fig

def _style_graph(fig, data: DataFrame = None):
    fig.update_layout({"plot_bgcolor": "#222", "paper_bgcolor": "#222"})
    fig.update_traces(line_color="#EC85B2")

    return fig
