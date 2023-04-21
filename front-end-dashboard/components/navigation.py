import dash_bootstrap_components as dbc
from dash import html
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
                        dbc.Col(
                            dbc.NavItem(dbc.NavLink("Node View", href="/node_view")),
                            width="auto",
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


node_typology = dbc.ListGroup(children=
    [
        dbc.ListGroupItem("IoT Node", className="typology-lvl1"),
        dbc.ListGroupItem("Node 2", className="typology-lvl2", href="/node_view/2"),
        dbc.ListGroupItem("Node 4", className="typology-lvl3", href="/node_view/4"),
        dbc.ListGroupItem("Node 5", className="typology-lvl3", href="/node_view/5"),
        dbc.ListGroupItem("Node 3", className="typology-lvl2", href="/node_view/3"),
        dbc.ListGroupItem("Node 6", className="typology-lvl3", href="/node_view/6"),
        dbc.ListGroupItem("Node 7", className="typology-lvl3", href="/node_view/7"),
    ],
)

timeframe_selector = html.Div(children=
    [
        dbc.Label("Timeframe"),
        dbc.Select(
            id="dropdown-timeframe",
            placeholder="15sec",
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
