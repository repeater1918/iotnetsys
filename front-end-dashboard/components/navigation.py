import dash_bootstrap_components as dbc
from dash import html, Output, Input, MATCH, State
from utils.data_connectors import get_topo_data, send_sessionid
from datetime import datetime, timedelta
import dash

navbar = dbc.Navbar(
    children=[
        dbc.Container(
            children=[
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.I(className="bi bi-tropical-storm icon")),
                            dbc.Col(dbc.NavbarBrand("IOTNetSys")),
                        ],
                        align="center",
                    ),
                    href="/",
                ),
                dbc.Row(
                    [
                        dbc.Col(dbc.Button(id='refresh-dash', children=[
                            html.I(className="bi bi-arrow-clockwise refresh-btn"),
                            'Refresh']),
                            width="auto"
                        ),

                        dbc.Col(dbc.Button(id='experiment-nav-btn', children=[
                            html.I(className="bi refresh-btn"),
                            'Archived Experiements'], href='/sessionlist'),
                            width="auto"
                        ),
                    ],
                    align="center",
                ),
            ],
            fluid=True,
        ),
    ],
    color="dark",
    dark=True,
    style={"padding-right": "16px", "padding-left": "16px"},
)


node_typology = dbc.ListGroup(id='node_nav', children=[html.Div()],)

timeframe_selector = html.Div(children=
    [
        dbc.Label("Timeframe"),
        dbc.Select(
            id="dropdown-timeframe",
            placeholder="choose (default 12hr)",
            value=43200,
            options=[
                {"label": "5sec", "value": "5"},
                {"label": "15sec", "value": "15"},
                {"label": "30sec", "value": "30"},
                {"label": "1min", "value": "60"},
                {"label": "5min", "value": "300"},
                {"label": "10min", "value": "600"},
                {"label": "15min", "value": "900"},
                {"label": "30min", "value": "1800"},
                {"label": "1hr", "value": "3600"},
                {"label": "2hr", "value": "7200"},
                {"label": "4hr", "value": "14400"},
                {"label": "6hr", "value": "21600"},
                {"label": "12hr", "value": "43200"},
            ],
            persistence=True,
            persistence_type='memory',
        ),
        dbc.Label("Deadline Loss Limit", style={'margin-top':'2.5rem'},),
        dbc.Select(
            id="dropdown-dlloss",
            placeholder="choose (default 100ms)",
            value=100,
            options=[
                {"label": "50ms", "value": "50"},
                {"label": "75ms", "value": "75"},
                {"label": "100ms", "value": "100"},
                {"label": "150ms", "value": "150"},
                {"label": "200ms", "value": "200"},
                {"label": "300ms", "value": "300"},
                {"label": "400ms", "value": "400"},
                {"label": "500ms", "value": "500"},
                {"label": "1sec", "value": "1000"},
                {"label": "5sec", "value": "5000"},
                {"label": "10sec", "value": "10000"},
                {"label": "30sec", "value": "30000"},
                {"label": "1min", "value": "60000"},
            ],
            persistence=True,
            persistence_type='memory',
        ),
    ],
    className="timeframe-menu",
)

nav_drawer = html.Div(className="fixed-width", children=[node_typology, timeframe_selector])

main_page_heading = dbc.Row(
            [
                dbc.Col(html.Div('Network Name')),
                dbc.Col(html.Div("Network Level Metrics"), style={'text-align': 'right'}),
            ], class_name='page-heading')


def top_page_heading(head_msg="Network Level"):
    """Draw the top page heading"""
    return (
            dbc.Row([
                dbc.Col(html.Div(head_msg)),
                dbc.Col(html.Div(f"{head_msg} Metrics"), style={'text-align': 'right'})], class_name='page-heading'),
                                                   
            )


@dash.callback(
        Output('node_nav', 'children'),
        [Input('node_nav','children'),
         Input('refresh-dash', 'n_clicks'),]
        )
def node_nav_callback(in_nav, n_clicks):   
    """Draw typology tree again based refresh button"""
    servers = get_topo_data(query="node_parent")
    nav = []
    servers_str = ','.join(map(str,servers))
    nav.append(dbc.ListGroupItem(f"Edge Server (Node: {servers_str})", className="typology-lvl1", href="/"))

    sensors = get_topo_data(query="node_sensor")
    #
    for i in sensors:
            nodeid = i['node']
            nav.append(dbc.ListGroupItem(f"IoT Node {nodeid}", className=f"typology-lvl2", href=f"/node_view/{nodeid}"))   

    return nav


@dash.callback(   
    Output({'type':'loading-output', 'page': MATCH}, "children"),
    [Input('refresh-dash', 'n_clicks')],
     State("usr-tz", "children"))
def update_refresh_loading_output_node(n_clicks, usrtz):
    """Update the last updated time in dashboard when user click refress"""
    #print(n_clicks)
    #print("usr timezone", usrtz)
    data_update = datetime.utcnow() - timedelta(minutes=usrtz)
    data_update = data_update.strftime("%d-%m-%Y %H:%M:%S")
    
    loading_out = [html.Div(f"Dashboard Last Updated: {data_update}"), ]
    return loading_out


@dash.callback(
     Output({'type':'experiment-id-div', 'page': MATCH}, "children"),
     Input('experiment-nav-btn', 'n_clicks'), 
     State('usr_session_data', 'data'),
    State("usr-tz", "children")
)
def update_experiment_selected(btn, data, usrtz):
    """Update the experiment div in graph page
    :param session_id_btn: button to select the view
    :param session_data: browser session data
    """
    res = None
    if isinstance(data,dict):
        if 'sessionid' in data.keys():
            res = send_sessionid(data['sessionid'])
    else:
        if btn == None:
            res = send_sessionid('')
        else:
            return dash.no_update
    
    if res == None:
         res = ''
    print(f"Update session {res} to AAS") 
    experiment_dt = datetime.fromisoformat(res)
    experiment_dt = experiment_dt - timedelta(minutes=usrtz)
    return "Experiment time: " + experiment_dt.strftime("%d-%m-%Y %H:%M:%S") 
     
