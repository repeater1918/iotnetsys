import plotly.express as px
from dash import dcc, html
import plotly.graph_objects as go

def get_parent_chg_graph(data = None, is_init=False, node_id=False, is_empty=False):

    if is_init:
        # first initialization of the graph, just need empty placeholder and identify the object in html tree
        graph_id = {"type": "graph-pc", "page": "node" if node_id else "network"} 
        title = f"Parent change value - Node: {node_id}" if node_id else "Avg Parent Change in Network"
        parent_chg_graph = _get_place_holder()

        return html.Div(
            children=[
                html.Div(title, className="graph-title"),
                dcc.Graph(id=graph_id, figure=parent_chg_graph),
            ]
        )
    
    if is_empty:
        #  update has occurred but not data, return a empty placeholder
        return _get_place_holder()
    
  
    if node_id:
        #  data is available and a node type graph is required, render graph for a node view       
        parent_chg_graph = go.Figure(
                        go.Indicator(
                            mode="number",
                            value=data['sub_type_value'].values[0],
                            number={"font":{"size":100}},
                            domain={"row":0, "column": 1},                          
                            title = {"text": f"<span style='font-size:0.9em;color:gray'> Average is {data['average'].values[0]} </span><br>"}
                            
                        ),                       
                        layout={"plot_bgcolor": "#222", "paper_bgcolor": "#222",},
                    ),
        

        return parent_chg_graph


    #  data is available and a node type graph is required, render graph for a node view
    parent_chg_graph =  go.Figure(
                        go.Indicator(
                            mode="number",
                            value=0,
                            domain={"x": [0, 1], "y": [0, 1]},                            
                            title={"text": "Parent Change Value"},
                           
                        ),
                        layout={"plot_bgcolor": "#222", "paper_bgcolor": "#222"},
                    ),

    return parent_chg_graph


def _get_place_holder():
    fig = go.Figure()
    return fig



