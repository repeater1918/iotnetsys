import dash
import plotly.express as px
from dash import Input, Output, State, dcc, html
import dash_bootstrap_templates as dbt
import dash_bootstrap_components as dbc
from views.graph_icmp_packets import get_icmp_graph
from views.graph_pdr import get_pdr_graph
from views.graph_queue_loss import get_queueloss_graph
from views.graph_pc_node_metric import get_parentchange_graph
from views.graph_hop_count import get_hop_cnt_graph
from utils.data_connectors import get_node_data, get_topo_data
import pandas as pd


dash.register_page(__name__, path_template='/node_view/<nodeid>')


def layout(nodeid):
    
    graph_duty_cycle = dcc.Graph(id={"type": "graph-duty-cycle", "page": "node"} )
    graph_e2e_metric = dcc.Graph(id={"type": "graph-e2e", "page": "node"}, figure=px.bar(title="Average End to End Delay"))
    graph_deadloss_metric = dcc.Graph(id={"type": "graph-deadloss", "page": "node"}, figure=px.bar(title="Deadline Loss Percentage"))
    graph_pc_node_metric = dcc.Graph(id=f"graph-pc-node", figure = px.bar(title="Parent Changes per Node"))

    return html.Div(
    children=[
        dbc.Row(dbc.Col(
            html.Div(dbc.Spinner(html.Div(id={'type':"loading-output", 'page': "node"})), className='loader-spinner'),
            xs=12
            )),
        dbc.Row(
            [
                dbc.Col(get_pdr_graph(is_init=True, node_id=nodeid), md=6, style={"margin-top": "16px"}),
                dbc.Col(get_queueloss_graph(is_init=True, node_id=nodeid), md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_e2e_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_deadloss_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(get_hop_cnt_graph(is_init=True, node_id=nodeid), md=6, style={"margin-top": "16px"}),                
                dbc.Col(get_icmp_graph(is_init=True, node_id=nodeid), md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_pc_node_metric, md=6, style={"margin-top": "16px"}),
                dbc.Col(graph_duty_cycle, md=6, style={"margin-top": "16px"}),
            ]),
       
        
    ]
)

#Callback

@dash.callback(Output(f"graph-hopcount-node", "figure"),
Output(f"graph-pc-node", "figure"),
[Input('url', 'pathname'), Input('refresh-dash', 'n_clicks')])
def update_node_graph(pathname, n_clicks):

    if pathname.split('/')[1] != 'node_view':
        return dash.no_update

    nodeid = int(pathname.split('/')[-1])

    api_data  = get_node_data(nodeid)    

    topo_api_data = get_topo_data()
    df_topo = pd.DataFrame(topo_api_data)
    if len(topo_api_data) == 0:
        hopcount_graph = get_hop_cnt_graph(is_empty=True, node_id=nodeid)[0]
    else:
        hopcount_graph = get_hop_cnt_graph(df_topo, node_id = nodeid)[0]

    df_pc_node = pd.DataFrame(api_data['pc_metric_node'])
    if len(api_data['pc_metric_node']) == 0:
        pc_node_graph = px.bar(title=f"Parent Changes - Node {nodeid}")
    else:
        pc_node_graph = px.bar(
            df_pc_node,
            x="node",
            y="total_parent_changes",
            title=f"Parent Changes - Node {nodeid}",
            labels={"node": "Node ID", "total_parent_changes": "Total Parent Changes"},
        )
        pc_node_graph.update_traces(marker_color="red")
        pc_node_graph.update_xaxes(type="category")

    return (hopcount_graph, pc_node_graph)
