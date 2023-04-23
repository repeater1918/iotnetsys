import plotly.express as px
from dash import dcc, html
from pandas import DataFrame
import dash_bootstrap_templates as dbt

dbt.load_figure_template("DARKLY")

def get_parentchange_graph(data=None, is_init=False, node_id=False, is_empty=False):

    if is_init:
        # first initialization of the graph, just need empty placeholder and identify the object in html tree
        graph_id = "graph-pc-node" if node_id else "graph-pc"
        #graph_id = "graph-pc-node"
        title = f"Number of parent changes - Node: {node_id}" if node_id else "Number of parent changes"
        #title = "Parent Changes per Node"
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
    
    parentchange_graph = px.bar(
            data,
            x="node",
            y="parent_changes",
            labels={"node": "Node ID", "parent_changes": "Number of parent changes"},
        )
    
    parentchange_graph = _style_graph(parentchange_graph, data)
    return parentchange_graph

def _get_place_holder():
    fig = _style_graph(px.bar())
    return fig

def _style_graph(fig, data: DataFrame = None):
    fig.update_layout({"plot_bgcolor": "#222", "paper_bgcolor": "#222"})
    if data is not None:
        fig.update_traces(line_color="blue")
    return fig