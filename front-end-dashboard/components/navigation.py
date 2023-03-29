import dash_bootstrap_components as dbc
from dash import html


navbar = dbc.Navbar(
    children=[
    dbc.Container(children=
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.I(className='bi bi-tropical-storm icon')),
                        dbc.Col(dbc.NavbarBrand("IOTNetSys")),
                    ],
                    align="center",
                ), href='/'
            ),

                dbc.Row(
                    [
                        dbc.Col(dbc.NavItem(dbc.NavLink("Node View", href="/node_view")), width='auto'),
                        dbc.Col(dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More Options", header=True),
                dbc.DropdownMenuItem("Settings", href="/settings"),
                dbc.DropdownMenuItem("Account", href="/account"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ), width='auto'),
                    ],
                    align="center",
                )




        ], fluid=True),

    ],
    color="dark",
    dark=True,
    style={'padding-right': '16px','padding-left': '16px'}
)