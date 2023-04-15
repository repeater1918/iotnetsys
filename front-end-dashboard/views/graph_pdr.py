import plotly.express as px
from dash import dcc, html
import plotly.graph_objects as go
from pandas import DataFrame

import dash_bootstrap_templates as dbt


dbt.load_figure_template("DARKLY")


def get_pdr_graph(data = None, is_init=False, node_id=False, is_empty=False):

    if is_init:
        # first initialization of the graph, just need empty placeholder and identify the object in html tree
        graph_id = "graph-pdr-node" if node_id else "graph-pdr"
        title = f"Packets Delivery Ratio - Node: {node_id}" if node_id else "Packets Delivery Ratio"
        pdr_graph = _get_place_holder()

        return html.Div(
            children=[
                html.Div(title, className="graph-title"),
                dcc.Graph(id=graph_id, figure=pdr_graph),
            ]
        )
    
    if is_empty:
        #  update has occurred but not data, return a empty placeholder
        return _get_place_holder()
    
    if node_id:
        #  data is available and a node type graph is required, render graph for a node view
        pdr_graph = px.area(
            data,
            x="env_timestamp",
            y="successful_packets_precentage",
            hover_name="node",
            markers=True,
            labels={"env_timestamp": "Time Invervals", "successful_packets_precentage": "Percentage Successful"},
        )
        pdr_graph = _style_graph(pdr_graph, data)

        return pdr_graph


    #  data is available and a node type graph is required, render graph for a node view
    pdr_graph = px.area(
            data,
            x="env_timestamp",
            y="successful_packets_precentage",
            title="Packet Delivery Ratios",
            markers=True,
            labels={"env_timestamp": "Time Invervals", "successful_packets_precentage": "Successful Packet %"},
        )
    pdr_graph = _style_graph(pdr_graph, data)

    return pdr_graph


def _get_place_holder():
    fig = _style_graph(px.line())
    return fig

def _style_graph(fig, data: DataFrame = None):
    fig.update_layout({"plot_bgcolor": "#222", "paper_bgcolor": "#222"})

    if data is not None:
        fig.update_layout(yaxis2=dict(title='Total Packets', overlaying='y', side='right'))
        fig.add_trace(go.Scatter(x=data['env_timestamp'], y=data['total_packets'], name='Total Packets', yaxis='y2'))

    return fig
