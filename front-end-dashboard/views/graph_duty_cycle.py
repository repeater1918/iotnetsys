import plotly.express as px
from dash import dcc, html
import plotly.graph_objects as go

def get_duty_cycle_graph(data = None, is_init=False, node_id=False, is_empty=False):
    """Drawing duty cycle graph
    :param data: meta data
    :param is_init True if graph is first loaded
    :param node_id: nodeid to view
    :param is_empty: draw graph with no data
    """
    if is_init:
        # first initialization of the graph, just need empty placeholder and identify the object in html tree
        graph_id = {"type": "graph-duty-cycle", "page": "node" if node_id else "network"} 
        title = f"Energy consumption - Node: {node_id}" if node_id else "Average Energy Consumption"
        duty_cycle_graph = _get_place_holder()

        return html.Div(
            children=[
                html.Div(title, className="graph-title"),
                dcc.Graph(id=graph_id, figure=duty_cycle_graph),
            ]
        )
    
    if is_empty:
        #  update has occurred but not data, return a empty placeholder
        return _get_place_holder()
    
  
    if node_id:
        #  data is available and a node type graph is required, render graph for a node view       
        duty_cycle_graph = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value= data.loc[0,"energy_cons"],                    
                    domain={"x": [0, 1], "y": [0, 1]},
                    delta={"reference": 100},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "steps": [
                            {"range": [0, 400], "color": "gray"},
                        ],
                    },
                ),

                layout={"plot_bgcolor": "#222", "paper_bgcolor": "#222"},
            )        
        

        return duty_cycle_graph


    #  data is available and a node type graph is required, render graph for a node view
    duty_cycle_graph = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value= data.loc[0,"energy_cons"],
                    
                    domain={"x": [0, 1], "y": [0, 1]},
                    delta={"reference": 100},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "steps": [
                            {"range": [0, 400], "color": "gray"},
                        ],
                    },
                ),

                layout={"plot_bgcolor": "#222", "paper_bgcolor": "#222"},
            )        

    return duty_cycle_graph


def _get_place_holder():
    fig = px.bar()
    return fig
