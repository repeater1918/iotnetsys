import plotly.graph_objects as go
from dash import dcc, html

import dash_bootstrap_templates as dbt

dbt.load_figure_template("DARKLY")

graph_duty_cycle = html.Div(
    children=[
        html.Div("Duty Cycle Levels", className='graph-title'),
        dcc.Graph(
            figure=go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=1000,
                    domain={"x": [0, 1], "y": [0, 1]},
                    delta={"reference": 1200},
                    title={"text": "Energy Level"},
                    gauge={
                        "axis": {"range": [None, 1200]},
                        "steps": [
                            {"range": [0, 400], "color": "gray"},
                        ],
                    },
                ),
                layout={"plot_bgcolor": "#222", "paper_bgcolor": "#222"},
            ),
        ),
    ]
)
