import plotly.express as px
from dash import dcc, html

import dash_bootstrap_templates as dbt


dbt.load_figure_template("DARKLY")


def get_icmp_graph(data = None, is_init=False, node_id=False, is_empty=False):

    if is_init:
        # first initialization of the graph, just need empty placeholder and identify the object in html tree
        graph_id = "graph-icmp-node" if node_id else "graph-icmp"
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
            labels={"env_timestamp": "Time", "sub_type_value": "Total ICMP Packets"},
            )
        
        icmp_graph = _style_graph(icmp_graph)

        return icmp_graph


    #  data is available and a node type graph is required, render graph for a node view
    icmp_graph = px.bar(
        data,
        x="node",
        y="sub_type_value",
        labels={"node": "Node ID", "sub_type_value": "Total ICMP Packets"},
    )
    icmp_graph = _style_graph(icmp_graph)

    return icmp_graph


def _get_place_holder():
    fig = _style_graph(px.bar())
    return fig

def _style_graph(fig):
    fig.update_traces(marker_color="green")
    fig.update_xaxes(type="category")
    fig.update_layout({"plot_bgcolor": "#222", "paper_bgcolor": "#222"})
    return fig
