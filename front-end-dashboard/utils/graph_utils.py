
import plotly.express as px
import plotly.graph_objects as go
from utils.data_connectors import get_node_data, get_network_data, get_topo_data
from views.graph_pc_node_metric import get_parent_chg_graph
from views.graph_icmp_packets import get_icmp_graph
from views.graph_pdr import get_pdr_graph
from views.graph_queue_loss import get_queueloss_graph
from views.graph_received_packets import get_receivedpackets_graph
from views.graph_hop_count import get_hop_cnt_graph
from views.graph_e2e import get_e2e_graph
from views.graph_deadloss import get_deadloss_graph
from views.network_topology import default_stylesheet
import pandas as pd
import dash
from dash import Output, Input, State, MATCH
from dash import html
import dash_bootstrap_components as dbc
from maindash import app


def get_common_graph(api_data, nodeid=None):    
    """Generate the graphs use in both network & node pages: pdr, icmp, queueloss, e2e, deadloss, duty-cycle"""
    
    df_pdr = pd.DataFrame(api_data['pdr_metric'])
    if len(api_data['pdr_metric']) == 0:
      pdr_graph = get_pdr_graph(is_empty=True, node_id=nodeid)
    else:  
        pdr_graph = get_pdr_graph(df_pdr, node_id=nodeid)

    df_icmp = pd.DataFrame(api_data['icmp_metric'])
    if len(api_data['icmp_metric']) == 0:
        icmp_graph = get_icmp_graph(is_empty=True, node_id=nodeid)
    else:
        icmp_graph = get_icmp_graph(df_icmp, node_id=nodeid)

    df_queueloss = pd.DataFrame(api_data['queueloss_metric'])
    if len(api_data['queueloss_metric']) == 0:
        queueloss_graph = get_queueloss_graph(is_empty=True, node_id=nodeid)
    else:
        queueloss_graph = get_queueloss_graph(df_queueloss, node_id=nodeid)    

    # for end to end delay
    df_e2e = pd.DataFrame(api_data['e2e_metric'])
    if len(api_data['e2e_metric']) == 0:
        e2e_graph = get_e2e_graph(is_empty=True, node_id=nodeid)
    else:  
        e2e_graph = get_e2e_graph(df_e2e, node_id=nodeid)

    # for deadline loss
    df_deadloss = pd.DataFrame(api_data['deadloss_metric'])
    if len(api_data['deadloss_metric']) == 0:
        deadloss_graph = get_deadloss_graph(is_empty=True, node_id=nodeid)
    else:  
        deadloss_graph = get_deadloss_graph(df_deadloss, node_id=nodeid)
        
    # for duty
    df_energy = pd.DataFrame(api_data['energy_cons_metric'])
    if len(api_data['energy_cons_metric']) == 0:
        graph_duty_cycle = px.bar(title="Energy Consumption")
    else:
        graph_duty_cycle = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value= 100 - df_energy.loc[0,"energy_cons"],
                    
                    domain={"x": [0, 1], "y": [0, 1]},
                    delta={"reference": 100},
                    title={"text": "Energy Consumption"},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "steps": [
                            {"range": [0, 400], "color": "gray"},
                        ],
                    },
                ),

                layout={"plot_bgcolor": "#222", "paper_bgcolor": "#222"},
            )        
      
    return (queueloss_graph, e2e_graph, deadloss_graph, graph_duty_cycle, pdr_graph, icmp_graph,)


#Callbacks for above graph
@app.callback(
Output({"type": "graph-queueloss", "page": MATCH}, "figure"),
Output({"type": "graph-e2e", "page": MATCH}, "figure"),
Output({"type":"graph-deadloss", "page": MATCH}, "figure"),
Output({"type":"graph-duty-cycle", "page": MATCH}, "figure"),
Output({"type":"graph-pdr", "page": MATCH}, "figure"),
Output({"type":"graph-icmp", "page": MATCH}, "figure"),
[Input('url', 'pathname'), Input('refresh-dash', 'n_clicks')])
def update_common_graphs(pathname, n_clicks):
    #print("Common graph is updating ")
    
    if pathname.split('/')[1] == 'node_view':
        nodeid = int(pathname.split('/')[-1])
        api_data  = get_node_data(nodeid)

    elif pathname == '/':
        nodeid = None
        api_data  = get_network_data()
       
    else:
        return dash.no_update
    
    queueloss_graph, e2e_graph, deadloss_graph, graph_duty_cycle, pdr_graph, icmp_graph = get_common_graph(api_data, nodeid)
    
    return (queueloss_graph, e2e_graph, deadloss_graph, graph_duty_cycle, pdr_graph, icmp_graph)


@app.callback(Output({"type": "graph-receivedpackets", "page": "network"}, "figure"),
[Input('url', 'pathname'), Input('refresh-dash', 'n_clicks')])
def update_network_graph(pathname, n_clicks):
    #print("Network specific graph is updating")
    if pathname != '/':
        return dash.no_update
    
    api_data  = get_network_data("received_metric")

    #graph for received packets    
    df_received = pd.DataFrame(api_data['received_metric'])   
    if len(api_data['received_metric']) == 0:
        received_graph = get_receivedpackets_graph(is_empty=True)
    else:
        received_graph = get_receivedpackets_graph(df_received)

    return received_graph


@app.callback(Output({"type":"graph-hopcount", "page": "node"}, "figure"),
Output({"type":"graph-pc", "page": "node"}, "figure"),
[Input('url', 'pathname'), Input('refresh-dash', 'n_clicks')])
def update_node_graph(pathname, n_clicks):
    
    if pathname.split('/')[1] != 'node_view':
        return dash.no_update

    nodeid = int(pathname.split('/')[-1])

    api_data  = get_node_data(nodeid, 'pc_metric')    

    topo_api_data = get_topo_data()

    df_topo = pd.DataFrame(topo_api_data)

    if len(topo_api_data) == 0:
        hopcount_graph = get_hop_cnt_graph(is_empty=True, node_id=nodeid)
    else:
        hopcount_graph = get_hop_cnt_graph(df_topo, node_id = nodeid)[0]
    
    df_pc_node = pd.DataFrame(api_data['pc_metric'])

    if len(api_data['pc_metric'])  == 0:
        pc_node_graph = get_parent_chg_graph(is_empty=True, node_id=nodeid)
    else:
        pc_node_graph = get_parent_chg_graph(df_pc_node, node_id = nodeid)[0]

    return (hopcount_graph, pc_node_graph)


@app.callback(
         Output("topology-graph", 'elements'),
         Output('topology-graph','layout'),
        [Input('topology-graph', 'elements'),
         Input('topology-graph', 'layout'),
         Input('url', 'pathname'), Input('refresh-dash', 'n_clicks')]
        
)
def topology_update(elements, layout, pathname, n_clicks):
    """Callback to extract topology and draw"""

    ele = []
    topo_api_data = get_topo_data()
    edge_servers = set()
    if pathname != '/':
        return dash.no_update
    for v in topo_api_data:     
        if v['role'] == 'server':
            edge_servers.add(f"{v['node']}")

        ele.append({'node': v['node'], 'parent': v['parent']})

    data_tuple = [tuple(id.values()) for id in ele] #Convert to tuple for cytoscape drawing
    # Drawing nodes 
    nodes = [{'data': {'id': str(node), 'label': str(node)}} for node,_ in data_tuple ]
    #Drawing links between source and its parent
    edges = [
        {'data': {'source': str(source), 'target': str(target)}}
        for source, target in [tup for tup in data_tuple if str(tup[0]) not in edge_servers] #Don't draw link for root node
        ]
    layout['roots'] = '#'+',#'.join(edge_servers)   
     
    return edges+nodes, layout



@app.callback(Output('topology-graph', 'stylesheet'),
                    Output('topo-toast', "is_open"),
                    Output('topo-toast', "header"),
                    Output("topo-toast", "children"),               
                    [Input('topology-graph', 'selectedNodeData'),              
                     Input('topology-graph', 'layout')],
                    [State('topo-toast', "is_open")])
def displayTapNodeData(data, layout, is_open):

        if data:
            #Node data[0]['id'] selected
            selected_node = data[0]['id']
            edge_servers = layout['roots'][1:].split(',#')
            new_styles = [
            {
                'selector': 'node[id = "{}"]'.format(selected_node),
                'style': {
                    'background-color': "green",                 
                }
            }]
            toast_hdr = [html.P(f"Node {selected_node}", className="mb-0", style={"color": "white"})]            
            is_open = True            
            if str(selected_node) not in edge_servers:
                toast_child = [html.P("I'm a sensor ", className="mb-0"),]
                toast_child.append(dbc.Button("Go to node view", size="sm mt-2", href=f"/node_view/{selected_node}"))
            else:
                 toast_child = [html.P("I'm a server", className="mb-0"),]

            
        else: 
            #De-select node
            toast_child = []
            is_open = False
            toast_hdr = ''
            new_styles = []

        return default_stylesheet + new_styles, is_open, toast_hdr, toast_child

