import dash_bootstrap_components as dbc
from dash import html, Output, Input, MATCH
import dash
from utils.data_connectors import get_topo_data, get_session_data
from datetime import datetime, timedelta
from maindash import app

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
                        
                        dbc.Col(
                            dbc.DropdownMenu(
                                children=[
                                    dbc.DropdownMenuItem("More Options", header=True),
                                    dbc.DropdownMenuItem("Settings", href="/settings"),
                                    dbc.DropdownMenuItem("Account", href="/account"),
                                ],
                                nav=True,
                                in_navbar=True,
                                label="More",
                            ),
                            width="auto",
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
            placeholder="choose (default 1min)",
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
            ],
        ),
        dbc.Label("Deadline Loss Limit", style={'margin-top':'2.5rem'},),
        dbc.Select(
            id="dropdown-dlloss",
            placeholder="choose (default 25ms)",
            options=[
                {"label": "25ms", "value": "25"},
                {"label": "50ms", "value": "50"},
                {"label": "75ms", "value": "75"},
                {"label": "100ms", "value": "100"},
                {"label": "150ms", "value": "150"},
                {"label": "200ms", "value": "200"},
                {"label": "300ms", "value": "300"},
                {"label": "400ms", "value": "400"},
                {"label": "500ms", "value": "500"},
                {"label": "1sec", "value": "1000"},
                {"label": "2sec", "value": "2000"},
                {"label": "5sec", "value": "5000"},
                {"label": "10sec", "value": "10000"},
                {"label": "20sec", "value": "20000"},
            ],
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
    return (
            dbc.Row([
                dbc.Col(html.Div(head_msg)),
                dbc.Col(html.Div(f"{head_msg} Metrics"), style={'text-align': 'right'})], class_name='page-heading'),
            dbc.Row(dbc.Col(html.Div(children=dash.page_container)))                                        
            )

@app.callback(
        Output('node_nav', 'children'),
        [Input('node_nav','children'),
         Input('refresh-dash', 'n_clicks'),]
        )
def node_nav_callback(in_nav, n_clicks):        
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


@app.callback(   
    Output({'type':'loading-output', 'page': MATCH}, "children"),
    [Input('refresh-dash', 'n_clicks'),
     Input("usr-tz", "children")])
def update_refresh_loading_output_node(n_clicks, usrtz):
    #print(n_clicks)
    #print("usr timezone", usrtz)
    data_update = datetime.utcnow() - timedelta(minutes=usrtz)
    data_update = data_update.strftime("%Y-%m-%d %H:%M:%S")
    
    sessions = get_session_data()
    last_session = sessions['Session Time'][-1]
    dt = datetime.fromisoformat(last_session)
    local_dt = (dt - timedelta(minutes=usrtz)).strftime("%Y-%m-%d %H:%M:%S")

    loading_out = [html.Div(f"Experiement Time: {local_dt}"), html.Div(f"Dashboard Last Updated: {data_update}"), ]
    return loading_out



