import plotly.express as px
from dash import dcc, html
import plotly.graph_objects as go
from pandas import DataFrame


def get_e2e_graph(data = None, is_init=False, node_id=False, is_empty=False):
    """Drawing end to end delay graph
    :param data: topology data
    :param is_init True if graph is first loaded
    :param node_id: nodeid to view
    :param is_empty: draw graph with no data
    """
    if is_init:
        # first initialization of the graph, just need empty placeholder and identify the object in html tree
        graph_id = {"type": "graph-e2e", "page": "node" if node_id else "network"} 
        title = f"Average End to End Delay - Node: {node_id}" if node_id else "Average End to End Delay"
        e2e_graph = _get_place_holder()

        return html.Div(
            children=[
                html.Div(title, className="graph-title"),
                dcc.Graph(id=graph_id, figure=e2e_graph),
            ]
        )
    
    if is_empty:
        #  update has occurred but not data, return a empty placeholder
        return _get_place_holder()
    
    if node_id:
        #  data is available and a node type graph is required, render graph for a node view
        e2e_graph = px.area(
            data,
            x="env_timestamp",
            y="average_delay",
            labels={"env_timestamp": "Time Invervals", "average_delay": "Milli-Seconds"},
        )
        e2e_graph = _style_graph(e2e_graph, data)

        return e2e_graph


    #  data is available and a node type graph is required, render graph for a node view
    e2e_graph = px.area(
            data,
            x="env_timestamp",
            y="average_delay",
            markers=True,
            labels={"env_timestamp": "Time Invervals", "average_delay": "Milli-Seconds"},
        )
    e2e_graph = _style_graph(e2e_graph, data)

    return e2e_graph


def _get_place_holder():
    fig = _style_graph(px.line())
    return fig

def _style_graph(fig, data: DataFrame = None):
    fig.update_layout({"plot_bgcolor": "#222", "paper_bgcolor": "#222"})
    fig.update_traces(line_color="#7A1BF6")

    return fig
